"""
Visualization Generator — creates charts from GitHub profile data.

Generates base64-encoded PNG images that can be embedded in JSON responses
and HTML templates. Uses matplotlib with a dark theme for consistency.
"""

import io
import base64
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

from backend.app.schemas.github_schemas import (
    LanguageStat,
    RepoDetail,
    ContributionData,
    Visualizations,
    SkillMatch,
)

logger = logging.getLogger(__name__)

# ─── Chart Theme Configuration ────────────────────────────────────────────────

DARK_BG = "#0d1117"
CARD_BG = "#161b22"
TEXT_COLOR = "#c9d1d9"
ACCENT_COLORS = [
    "#58a6ff",  # Blue
    "#3fb950",  # Green
    "#d29922",  # Yellow
    "#f85149",  # Red
    "#bc8cff",  # Purple
    "#79c0ff",  # Light blue
    "#56d364",  # Light green
    "#e3b341",  # Light yellow
    "#ff7b72",  # Light red
    "#d2a8ff",  # Light purple
    "#a5d6ff",  # Pale blue
    "#7ee787",  # Pale green
]

# GitHub contribution colors (dark to light green)
CONTRIB_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def _fig_to_base64(fig: plt.Figure) -> str:
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        bbox_inches="tight",
        dpi=150,
        facecolor=fig.get_facecolor(),
        edgecolor="none",
    )
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _apply_dark_theme(ax: plt.Axes):
    """Apply consistent dark theme to axes."""
    ax.set_facecolor(CARD_BG)
    ax.tick_params(colors=TEXT_COLOR, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("#30363d")
    ax.spines["left"].set_color("#30363d")
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.title.set_color(TEXT_COLOR)


class Visualizer:
    """Generates chart visualizations from GitHub profile data."""

    def generate_all(
        self,
        language_stats: list[LanguageStat],
        repos: list[RepoDetail],
        contributions: ContributionData | None,
        skill_matches: list[SkillMatch] | None = None,
    ) -> Visualizations:
        """Generate all available visualizations."""
        viz = Visualizations()

        try:
            viz.language_chart = self._create_language_chart(language_stats)
        except Exception as e:
            logger.error(f"Failed to create language chart: {e}")

        try:
            viz.stars_chart = self._create_stars_chart(repos)
        except Exception as e:
            logger.error(f"Failed to create stars chart: {e}")

        if contributions and contributions.contribution_calendar:
            try:
                viz.contribution_heatmap = self._create_contribution_heatmap(
                    contributions
                )
            except Exception as e:
                logger.error(f"Failed to create contribution heatmap: {e}")

            try:
                viz.activity_timeline = self._create_activity_timeline(
                    contributions
                )
            except Exception as e:
                logger.error(f"Failed to create activity timeline: {e}")

        if skill_matches:
            try:
                viz.skill_radar = self._create_skill_radar(skill_matches)
            except Exception as e:
                logger.error(f"Failed to create skill radar: {e}")

        return viz

    # ═══════════════════════════════════════════════════════════════════════════
    # Chart Generators
    # ═══════════════════════════════════════════════════════════════════════════

    def _create_language_chart(
        self, language_stats: list[LanguageStat]
    ) -> Optional[str]:
        """Create a donut chart showing language distribution."""
        if not language_stats:
            return None

        # Take top 8 and group rest as "Other"
        top = language_stats[:8]
        other_pct = sum(s.percentage for s in language_stats[8:])

        labels = [s.language for s in top]
        sizes = [s.percentage for s in top]
        colors = ACCENT_COLORS[: len(top)]

        if other_pct > 0:
            labels.append("Other")
            sizes.append(round(other_pct, 2))
            colors.append("#484f58")

        fig, ax = plt.subplots(figsize=(8, 6), facecolor=DARK_BG)
        ax.set_facecolor(DARK_BG)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct=lambda pct: f"{pct:.1f}%",
            startangle=90,
            pctdistance=0.78,
            wedgeprops=dict(width=0.4, edgecolor=DARK_BG, linewidth=2),
        )

        for autotext in autotexts:
            autotext.set_color(TEXT_COLOR)
            autotext.set_fontsize(8)
            autotext.set_fontweight("bold")

        # Legend
        legend = ax.legend(
            wedges,
            [f"{l} ({s:.1f}%)" for l, s in zip(labels, sizes)],
            title="Languages",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9,
            frameon=False,
        )
        legend.get_title().set_color(TEXT_COLOR)
        legend.get_title().set_fontsize(11)
        legend.get_title().set_fontweight("bold")
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)

        ax.set_title(
            "Language Distribution",
            fontsize=14,
            fontweight="bold",
            color=TEXT_COLOR,
            pad=20,
        )

        return _fig_to_base64(fig)

    def _create_stars_chart(
        self, repos: list[RepoDetail]
    ) -> Optional[str]:
        """Create a horizontal bar chart of top repos by stars."""
        # Filter repos with stars, sort descending
        starred = [r for r in repos if r.stars > 0]
        starred.sort(key=lambda r: r.stars, reverse=True)
        top = starred[:10]

        if not top:
            return None

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=DARK_BG)
        _apply_dark_theme(ax)

        names = [r.name[:25] for r in reversed(top)]
        stars = [r.stars for r in reversed(top)]
        forks = [r.forks for r in reversed(top)]

        y_pos = np.arange(len(names))
        bar_height = 0.35

        bars1 = ax.barh(
            y_pos - bar_height / 2,
            stars,
            bar_height,
            label="⭐ Stars",
            color=ACCENT_COLORS[2],
            edgecolor="none",
            zorder=3,
        )
        bars2 = ax.barh(
            y_pos + bar_height / 2,
            forks,
            bar_height,
            label="🍴 Forks",
            color=ACCENT_COLORS[0],
            edgecolor="none",
            zorder=3,
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=9)
        ax.set_xlabel("Count", fontsize=10)
        ax.set_title(
            "Top Repositories by Stars",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        legend = ax.legend(
            loc="lower right",
            fontsize=9,
            frameon=False,
        )
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)

        ax.grid(axis="x", alpha=0.1, color="#30363d", zorder=0)

        return _fig_to_base64(fig)

    def _create_contribution_heatmap(
        self, contributions: ContributionData
    ) -> Optional[str]:
        """Create a GitHub-style contribution heatmap."""
        calendar = contributions.contribution_calendar
        if not calendar:
            return None

        # Build the heatmap grid (7 rows x N weeks)
        weeks = []
        for week_data in calendar:
            days = week_data.get("days", [])
            week_counts = []
            for day in days:
                week_counts.append(day.get("contributionCount", 0))
            # Pad to 7 days if needed
            while len(week_counts) < 7:
                week_counts.append(0)
            weeks.append(week_counts[:7])

        if not weeks:
            return None

        # Convert to numpy array (transposed: 7 rows x N columns)
        data = np.array(weeks).T

        fig, ax = plt.subplots(figsize=(16, 3), facecolor=DARK_BG)
        ax.set_facecolor(DARK_BG)

        # Create custom colormap (GitHub green theme)
        cmap = mcolors.ListedColormap(CONTRIB_COLORS)
        max_val = max(data.max(), 1)
        bounds = [0, 1, max_val * 0.25, max_val * 0.5, max_val * 0.75, max_val + 1]
        norm = mcolors.BoundaryNorm(bounds, cmap.N)

        im = ax.pcolormesh(
            data,
            cmap=cmap,
            norm=norm,
            edgecolors=DARK_BG,
            linewidth=2,
        )

        ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
        ax.set_yticklabels(
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            fontsize=8,
        )
        ax.tick_params(colors=TEXT_COLOR, length=0)
        ax.invert_yaxis()

        # Remove x ticks (too dense)
        ax.set_xticks([])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        ax.set_title(
            f"Contribution Activity ({contributions.total_contributions} contributions)",
            fontsize=13,
            fontweight="bold",
            color=TEXT_COLOR,
            pad=10,
        )

        # Add legend squares
        legend_elements = []
        for i, color in enumerate(CONTRIB_COLORS):
            from matplotlib.patches import Patch

            legend_elements.append(Patch(facecolor=color, edgecolor="#30363d"))
        legend = ax.legend(
            legend_elements,
            ["0", "Low", "Med", "High", "Max"],
            loc="lower right",
            ncol=5,
            fontsize=7,
            frameon=False,
            handlelength=1,
            handleheight=1,
        )
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)

        return _fig_to_base64(fig)

    def _create_activity_timeline(
        self, contributions: ContributionData
    ) -> Optional[str]:
        """Create a line chart showing contribution activity over time."""
        calendar = contributions.contribution_calendar
        if not calendar:
            return None

        # Aggregate contributions per week
        weekly_totals = []
        for week_data in calendar:
            days = week_data.get("days", [])
            total = sum(d.get("contributionCount", 0) for d in days)
            weekly_totals.append(total)

        if not weekly_totals:
            return None

        fig, ax = plt.subplots(figsize=(12, 4), facecolor=DARK_BG)
        _apply_dark_theme(ax)

        x = range(len(weekly_totals))

        # Fill area under curve
        ax.fill_between(
            x,
            weekly_totals,
            alpha=0.3,
            color=ACCENT_COLORS[1],
            zorder=2,
        )

        # Line
        ax.plot(
            x,
            weekly_totals,
            color=ACCENT_COLORS[1],
            linewidth=1.5,
            zorder=3,
        )

        # Moving average line
        if len(weekly_totals) > 4:
            window = 4
            moving_avg = np.convolve(
                weekly_totals, np.ones(window) / window, mode="valid"
            )
            ax.plot(
                range(window - 1, len(weekly_totals)),
                moving_avg,
                color=ACCENT_COLORS[0],
                linewidth=2,
                linestyle="--",
                label="4-week avg",
                zorder=4,
            )

        ax.set_xlabel("Weeks", fontsize=10)
        ax.set_ylabel("Contributions", fontsize=10)
        ax.set_title(
            "Weekly Activity Timeline",
            fontsize=14,
            fontweight="bold",
            pad=15,
        )

        ax.grid(axis="y", alpha=0.1, color="#30363d", zorder=0)

        if len(weekly_totals) > 4:
            legend = ax.legend(
                loc="upper right",
                fontsize=9,
                frameon=False,
            )
            for text in legend.get_texts():
                text.set_color(TEXT_COLOR)

        return _fig_to_base64(fig)

    def _create_skill_radar(
        self, skill_matches: list[SkillMatch]
    ) -> Optional[str]:
        """Create a radar/spider chart comparing required vs found skills."""
        if not skill_matches:
            return None

        # Limit to top 12 skills for readability
        skills = skill_matches[:12]

        labels = [s.skill for s in skills]
        values = [1.0 if s.found else 0.0 for s in skills]

        num_vars = len(labels)
        if num_vars < 3:
            return None  # Radar chart needs at least 3 points

        # Compute angles
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values_plot = values + [values[0]]
        angles += [angles[0]]

        fig, ax = plt.subplots(
            figsize=(8, 8),
            subplot_kw=dict(polar=True),
            facecolor=DARK_BG,
        )
        ax.set_facecolor(CARD_BG)

        # Draw the radar
        ax.fill(angles, values_plot, color=ACCENT_COLORS[1], alpha=0.25)
        ax.plot(
            angles,
            values_plot,
            color=ACCENT_COLORS[1],
            linewidth=2,
        )

        # Mark found/missing
        for i, (angle, value) in enumerate(zip(angles[:-1], values)):
            color = ACCENT_COLORS[1] if value > 0 else ACCENT_COLORS[3]
            ax.scatter(
                angle,
                value,
                color=color,
                s=80,
                zorder=5,
                edgecolors="white",
                linewidth=1,
            )

        # Customize labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=9, color=TEXT_COLOR)

        ax.set_yticks([0, 0.5, 1.0])
        ax.set_yticklabels(["", "", ""], fontsize=8)
        ax.set_ylim(0, 1.1)

        # Grid styling
        ax.grid(color="#30363d", alpha=0.3)
        ax.spines["polar"].set_color("#30363d")

        matched = sum(values)
        total = len(values)
        ax.set_title(
            f"Skill Match Radar ({int(matched)}/{total} matched)",
            fontsize=14,
            fontweight="bold",
            color=TEXT_COLOR,
            pad=20,
        )

        # Legend
        from matplotlib.patches import Patch

        legend_elements = [
            Patch(facecolor=ACCENT_COLORS[1], label="Skill Found"),
            Patch(facecolor=ACCENT_COLORS[3], label="Skill Missing"),
        ]
        legend = ax.legend(
            handles=legend_elements,
            loc="lower right",
            bbox_to_anchor=(1.2, -0.05),
            fontsize=9,
            frameon=False,
        )
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)

        return _fig_to_base64(fig)
