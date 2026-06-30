"""
AI Analyzer — matches candidate GitHub profile against a job description.

Primary: Google Gemini API for intelligent analysis.
Fallback: Keyword-based matching when Gemini is unavailable or errors out.
"""

import json
import re
import logging
from typing import Any

from app.config import settings
from app.models.schemas import (
    AIAnalysis,
    SkillMatch,
    LanguageStat,
    RepoDetail,
    GitHubProfile,
    ContributionData,
    ProfileScores,
)

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyzes candidate profiles against job descriptions."""

    def __init__(self):
        self.gemini_available = False
        self.model = None

        if settings.has_gemini:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
                self.gemini_available = True
                logger.info("Gemini AI initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
                self.gemini_available = False

    async def analyze(
        self,
        job_description: str,
        profile: GitHubProfile,
        repos: list[RepoDetail],
        language_stats: list[LanguageStat],
        contributions: ContributionData | None,
        scores: ProfileScores,
        extracted_skills: list[str],
    ) -> AIAnalysis:
        """
        Analyze candidate profile against job description.
        Uses Gemini if available, falls back to keyword matching.
        """
        if self.gemini_available:
            try:
                result = await self._analyze_with_gemini(
                    job_description,
                    profile,
                    repos,
                    language_stats,
                    contributions,
                    scores,
                    extracted_skills,
                )
                if result:
                    return result
                logger.warning("Gemini analysis returned None, falling back to keyword matching")
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}, falling back to keyword matching")

        # Fallback: keyword-based matching
        return self._analyze_with_keywords(
            job_description,
            profile,
            repos,
            language_stats,
            extracted_skills,
            scores,
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # Gemini AI Analysis
    # ═══════════════════════════════════════════════════════════════════════════

    async def _analyze_with_gemini(
        self,
        job_description: str,
        profile: GitHubProfile,
        repos: list[RepoDetail],
        language_stats: list[LanguageStat],
        contributions: ContributionData | None,
        scores: ProfileScores,
        extracted_skills: list[str],
    ) -> AIAnalysis | None:
        """Use Gemini to generate intelligent analysis."""
        if not self.model:
            return None

        # Build structured profile summary for Gemini
        profile_summary = self._build_profile_summary(
            profile, repos, language_stats, contributions, scores, extracted_skills
        )

        prompt = f"""You are an expert technical recruiter AI. Analyze the following GitHub profile against the job description and provide a detailed assessment.

## Job Description
{job_description}

## Candidate GitHub Profile
{profile_summary}

## Instructions
Analyze how well this candidate matches the job description. Return your analysis as a JSON object with EXACTLY this structure (no markdown, no code fences, just raw JSON):

{{
    "match_percentage": <number 0-100>,
    "matching_skills": [
        {{"skill": "<skill name>", "found": true, "evidence": ["<repo name or detail>"]}},
    ],
    "missing_skills": ["<skill required by JD but not found>"],
    "relevant_projects": [
        {{"repo_name": "<name>", "relevance": "<why this repo is relevant to the JD>"}},
    ],
    "strengths": ["<candidate strength relative to JD>"],
    "weaknesses": ["<candidate gap relative to JD>"],
    "recommendation": "<one of: Strong Match, Good Match, Partial Match, Weak Match>",
    "summary": "<2-3 paragraph recruiter-friendly narrative summary>"
}}

Be specific and reference actual repository names and technologies found in the profile. Be fair but honest in your assessment.
"""

        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text.strip()

            # Clean up response (remove markdown code fences if present)
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

            data = json.loads(text)

            # Parse matching skills
            matching_skills = []
            for skill_data in data.get("matching_skills", []):
                matching_skills.append(
                    SkillMatch(
                        skill=skill_data.get("skill", ""),
                        found=skill_data.get("found", True),
                        evidence=skill_data.get("evidence", []),
                    )
                )

            # Parse relevant projects
            relevant_projects = data.get("relevant_projects", [])

            return AIAnalysis(
                match_percentage=float(data.get("match_percentage", 0)),
                matching_skills=matching_skills,
                missing_skills=data.get("missing_skills", []),
                relevant_projects=relevant_projects,
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                recommendation=data.get("recommendation", "Unknown"),
                summary=data.get("summary", ""),
                analysis_method="gemini",
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            return None

    def _build_profile_summary(
        self,
        profile: GitHubProfile,
        repos: list[RepoDetail],
        language_stats: list[LanguageStat],
        contributions: ContributionData | None,
        scores: ProfileScores,
        extracted_skills: list[str],
    ) -> str:
        """Build a structured text summary of the profile for the AI prompt."""
        lines = []

        # Basic info
        lines.append(f"**Username**: {profile.username}")
        if profile.name:
            lines.append(f"**Name**: {profile.name}")
        if profile.bio:
            lines.append(f"**Bio**: {profile.bio}")
        if profile.location:
            lines.append(f"**Location**: {profile.location}")
        if profile.company:
            lines.append(f"**Company**: {profile.company}")
        lines.append(f"**Followers**: {profile.followers}")
        lines.append(f"**Public Repos**: {profile.public_repos}")
        lines.append(f"**Account Created**: {profile.created_at}")
        lines.append("")

        # Scores
        lines.append(f"**Overall Score**: {scores.overall_score}/100")
        lines.append(f"**Activity Score**: {scores.activity_score}/100")
        lines.append(f"**Quality Score**: {scores.quality_score}/100")
        lines.append("")

        # Languages
        lines.append("**Top Languages**:")
        for stat in language_stats[:10]:
            lines.append(
                f"  - {stat.language}: {stat.percentage}% ({stat.repo_count} repos)"
            )
        lines.append("")

        # Skills
        lines.append(f"**Extracted Skills/Technologies**: {', '.join(extracted_skills[:30])}")
        lines.append("")

        # Contributions
        if contributions:
            lines.append(f"**Total Contributions (last year)**: {contributions.total_contributions}")
            lines.append(f"**Longest Streak**: {contributions.longest_streak} days")
            lines.append(f"**Current Streak**: {contributions.current_streak} days")
            lines.append("")

        # Top repositories
        lines.append("**Top Repositories** (by quality score):")
        top_repos = sorted(repos, key=lambda r: r.stars, reverse=True)[:15]
        for repo in top_repos:
            desc = repo.description or "No description"
            langs = ", ".join(repo.languages.keys()) if repo.languages else (repo.language or "N/A")
            topics = ", ".join(repo.topics) if repo.topics else "None"
            lines.append(
                f"  - **{repo.name}** ⭐{repo.stars} 🍴{repo.forks} | "
                f"Languages: {langs} | Topics: {topics} | "
                f"Description: {desc[:100]}"
            )
            if repo.readme_excerpt:
                excerpt = repo.readme_excerpt[:200].replace("\n", " ")
                lines.append(f"    README excerpt: {excerpt}")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # Keyword-Based Fallback Analysis
    # ═══════════════════════════════════════════════════════════════════════════

    def _analyze_with_keywords(
        self,
        job_description: str,
        profile: GitHubProfile,
        repos: list[RepoDetail],
        language_stats: list[LanguageStat],
        extracted_skills: list[str],
        scores: ProfileScores,
    ) -> AIAnalysis:
        """Keyword-based matching when Gemini is unavailable."""

        # Extract required skills from job description
        jd_skills = self._extract_skills_from_text(job_description)

        # Build candidate skill set (lowercase for matching)
        candidate_skills = set(s.lower() for s in extracted_skills)
        candidate_langs = set(s.language.lower() for s in language_stats)
        all_candidate_skills = candidate_skills | candidate_langs

        # Match skills
        matching_skills = []
        missing_skills = []

        for skill in jd_skills:
            skill_lower = skill.lower()
            # Check for exact or fuzzy match
            found = False
            evidence = []

            if skill_lower in all_candidate_skills:
                found = True
                # Find repos demonstrating this skill
                for repo in repos:
                    repo_langs = set(
                        l.lower() for l in repo.languages.keys()
                    )
                    repo_topics = set(t.lower() for t in repo.topics)
                    if (
                        skill_lower in repo_langs
                        or skill_lower in repo_topics
                        or (repo.language and repo.language.lower() == skill_lower)
                        or (
                            repo.readme_excerpt
                            and skill_lower in repo.readme_excerpt.lower()
                        )
                    ):
                        evidence.append(repo.name)

            # Check aliases (e.g., "js" -> "javascript")
            if not found:
                aliases = self._get_skill_aliases(skill_lower)
                for alias in aliases:
                    if alias in all_candidate_skills:
                        found = True
                        evidence.append(f"(via {alias})")
                        break

            matching_skills.append(
                SkillMatch(
                    skill=skill,
                    found=found,
                    evidence=evidence[:5],
                )
            )

            if not found:
                missing_skills.append(skill)

        # Calculate match percentage
        total_jd_skills = max(len(jd_skills), 1)
        matched_count = sum(1 for s in matching_skills if s.found)
        match_percentage = round((matched_count / total_jd_skills) * 100, 1)

        # Find relevant projects
        relevant_projects = self._find_relevant_projects(repos, jd_skills)

        # Generate strengths and weaknesses
        strengths = self._identify_strengths(
            profile, repos, language_stats, scores, jd_skills
        )
        weaknesses = self._identify_weaknesses(
            missing_skills, scores, repos
        )

        # Determine recommendation
        if match_percentage >= 75:
            recommendation = "Strong Match"
        elif match_percentage >= 50:
            recommendation = "Good Match"
        elif match_percentage >= 30:
            recommendation = "Partial Match"
        else:
            recommendation = "Weak Match"

        # Generate summary
        summary = self._generate_keyword_summary(
            profile,
            match_percentage,
            matched_count,
            total_jd_skills,
            strengths,
            weaknesses,
            recommendation,
        )

        return AIAnalysis(
            match_percentage=match_percentage,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            relevant_projects=relevant_projects,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendation=recommendation,
            summary=summary,
            analysis_method="keyword",
        )

    def _extract_skills_from_text(self, text: str) -> list[str]:
        """Extract technology/skill keywords from a text (job description)."""
        from app.services.data_processor import TECH_KEYWORDS

        found: set[str] = set()
        text_lower = text.lower()

        for tech in TECH_KEYWORDS:
            pattern = r"\b" + re.escape(tech) + r"\b"
            if re.search(pattern, text_lower):
                found.add(tech)

        # Also extract capitalized tech names (e.g., "React", "Docker")
        words = re.findall(r"\b[A-Z][a-zA-Z+#.]+\b", text)
        for word in words:
            if word.lower() in TECH_KEYWORDS:
                found.add(word.lower())

        return sorted(found)

    def _get_skill_aliases(self, skill: str) -> list[str]:
        """Return known aliases for a skill name."""
        alias_map = {
            "javascript": ["js", "ecmascript", "es6"],
            "typescript": ["ts"],
            "python": ["py", "python3"],
            "golang": ["go"],
            "go": ["golang"],
            "cpp": ["c++"],
            "c++": ["cpp"],
            "csharp": ["c#"],
            "c#": ["csharp"],
            "reactjs": ["react"],
            "react": ["reactjs", "react.js"],
            "vuejs": ["vue"],
            "vue": ["vuejs", "vue.js"],
            "nextjs": ["next.js"],
            "next.js": ["nextjs"],
            "expressjs": ["express"],
            "express": ["expressjs", "express.js"],
            "nodejs": ["node.js", "node"],
            "node.js": ["nodejs", "node"],
            "postgresql": ["postgres", "psql"],
            "postgres": ["postgresql"],
            "mongodb": ["mongo"],
            "kubernetes": ["k8s"],
            "k8s": ["kubernetes"],
            "machine-learning": ["ml"],
            "deep-learning": ["dl"],
            "artificial-intelligence": ["ai"],
            "tailwindcss": ["tailwind"],
            "tailwind": ["tailwindcss"],
            "scikit-learn": ["sklearn"],
            "sklearn": ["scikit-learn"],
        }
        return alias_map.get(skill, [])

    def _find_relevant_projects(
        self,
        repos: list[RepoDetail],
        jd_skills: list[str],
    ) -> list[dict[str, str]]:
        """Find repos that are most relevant to the job description."""
        relevant = []
        jd_skills_lower = set(s.lower() for s in jd_skills)

        for repo in repos:
            repo_techs = set()
            for lang in repo.languages:
                repo_techs.add(lang.lower())
            for topic in repo.topics:
                repo_techs.add(topic.lower())
            if repo.language:
                repo_techs.add(repo.language.lower())

            overlap = repo_techs & jd_skills_lower
            if overlap:
                relevant.append(
                    {
                        "repo_name": repo.name,
                        "relevance": f"Uses {', '.join(sorted(overlap))}. "
                        + (repo.description or "No description"),
                    }
                )

        # Sort by number of matching skills
        relevant.sort(
            key=lambda x: len(x["relevance"].split(",")),
            reverse=True,
        )
        return relevant[:10]

    def _identify_strengths(
        self,
        profile: GitHubProfile,
        repos: list[RepoDetail],
        language_stats: list[LanguageStat],
        scores: ProfileScores,
        jd_skills: list[str],
    ) -> list[str]:
        """Identify candidate strengths relative to the JD."""
        strengths = []

        if scores.activity_score >= 70:
            strengths.append(
                f"Highly active contributor (activity score: {scores.activity_score}/100)"
            )
        if scores.quality_score >= 70:
            strengths.append(
                f"High-quality repositories (quality score: {scores.quality_score}/100)"
            )

        total_stars = sum(r.stars for r in repos)
        if total_stars > 50:
            strengths.append(
                f"Popular open source contributor ({total_stars} total stars)"
            )

        if len(language_stats) >= 5:
            top_langs = [s.language for s in language_stats[:5]]
            strengths.append(
                f"Versatile developer proficient in {', '.join(top_langs)}"
            )

        if profile.followers >= 50:
            strengths.append(
                f"Established GitHub presence ({profile.followers} followers)"
            )

        if profile.public_repos >= 20:
            strengths.append(
                f"Extensive portfolio ({profile.public_repos} public repositories)"
            )

        return strengths[:6]

    def _identify_weaknesses(
        self,
        missing_skills: list[str],
        scores: ProfileScores,
        repos: list[RepoDetail],
    ) -> list[str]:
        """Identify candidate gaps relative to the JD."""
        weaknesses = []

        if missing_skills:
            skills_preview = ", ".join(missing_skills[:5])
            if len(missing_skills) > 5:
                skills_preview += f" (+{len(missing_skills) - 5} more)"
            weaknesses.append(f"Missing required skills: {skills_preview}")

        if scores.activity_score < 30:
            weaknesses.append("Low recent activity on GitHub")

        if scores.quality_score < 30:
            weaknesses.append(
                "Repositories lack documentation and quality indicators"
            )

        if scores.consistency_score < 30:
            weaknesses.append("Inconsistent contribution history")

        if not any(r.stars > 0 for r in repos):
            weaknesses.append("No repositories have received community stars")

        return weaknesses[:5]

    def _generate_keyword_summary(
        self,
        profile: GitHubProfile,
        match_pct: float,
        matched: int,
        total: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendation: str,
    ) -> str:
        """Generate a recruiter-friendly summary from keyword analysis."""
        name = profile.name or profile.username

        summary = (
            f"{name} demonstrates a {match_pct}% skill match with the job requirements, "
            f"matching {matched} out of {total} required technologies identified in the job description. "
        )

        if strengths:
            summary += (
                f"Key strengths include: {strengths[0].lower()}. "
            )

        if weaknesses:
            summary += f"Areas for consideration: {weaknesses[0].lower()}. "

        summary += (
            f"\n\nOverall recommendation: **{recommendation}**. "
            f"This analysis was performed using keyword-based matching. "
            f"For a more nuanced assessment, configure the Gemini API key."
        )

        return summary
