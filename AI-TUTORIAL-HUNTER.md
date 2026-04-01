# AI Tutorial Hunter

## Project Overview

**AI Tutorial Hunter** is an agentic AI system that autonomously discovers, ranks, and curates the most trending AI tutorials, guides, and learning resources across the internet. It identifies what people are actively searching for, what topics are gaining momentum, and surfaces the highest-quality educational content to help learners stay ahead of the curve.

---

## Problem Statement

The AI field moves at breakneck speed. New frameworks, models, techniques, and paradigms emerge weekly. Learners face three core challenges:

1. **Discovery overload** — Too many tutorials, no way to know which are worth the time
2. **Trend blindness** — By the time a topic appears in a curated newsletter, the early-mover advantage is gone
3. **Quality variance** — Search results mix outdated, shallow, or clickbait content with genuinely valuable guides

AI Tutorial Hunter solves this by acting as an always-on research agent that surfaces what matters, when it matters.

---

## Core Capabilities

### 1. Trend Detection Engine
- Monitors search trends (Google Trends, Reddit, Hacker News, X/Twitter, Stack Overflow, GitHub trending)
- Tracks rising queries related to AI/ML/LLM/GenAI topics
- Identifies emerging topics before they peak (early signal detection)
- Analyzes search volume velocity — not just what's popular, but what's *accelerating*

### 2. Content Discovery Agent
- Crawls and indexes tutorials from:
  - YouTube (AI channels, new uploads, view velocity)
  - Medium, Dev.to, Towards Data Science
  - GitHub repos with tutorial/learning focus
  - Official documentation sites (OpenAI, Anthropic, Hugging Face, LangChain, etc.)
  - Course platforms (fast.ai, DeepLearning.AI, Coursera, Udemy trending)
  - ArXiv papers with companion tutorials/code
  - Blog posts from AI researchers and engineers
- Extracts metadata: title, topic, difficulty level, publish date, engagement metrics

### 3. Quality Scoring System
- **Relevance score** — How well does the content match the trending topic?
- **Freshness score** — How recent is the content? Is it up-to-date with latest APIs/models?
- **Engagement score** — Views, stars, upvotes, comments, shares relative to age
- **Depth score** — Does it provide hands-on code, or is it surface-level overview?
- **Author credibility** — Track record, affiliations, community reputation
- **Composite rank** — Weighted combination of all scores, configurable by user preference

### 4. Curation & Delivery
- Daily/weekly digest of top trending AI tutorials
- Categorized by topic: LLMs, Computer Vision, Agents, RAG, Fine-tuning, MLOps, etc.
- Difficulty tags: Beginner, Intermediate, Advanced
- Delivery channels: Email digest, Web dashboard, API endpoint, Slack/Discord bot
- Personalization: Users can set topic preferences, skill level, and content format preferences

### 5. Gap Analysis
- Identifies topics people are searching for but few quality tutorials exist
- Flags underserved areas — potential content creation opportunities
- Tracks "most asked but least answered" questions across forums

---

## Architecture

```
ai-tutorial-hunter/
├── agents/                  # Autonomous agent modules
│   ├── trend_detector.py    # Monitors trend sources, identifies rising topics
│   ├── content_crawler.py   # Discovers and extracts tutorial content
│   ├── quality_scorer.py    # Scores and ranks discovered content
│   ├── gap_analyzer.py      # Identifies underserved topics
│   └── orchestrator.py      # Coordinates agent workflows
├── sources/                 # Source-specific adapters
│   ├── google_trends.py
│   ├── reddit.py
│   ├── hackernews.py
│   ├── youtube.py
│   ├── github.py
│   ├── arxiv.py
│   ├── medium.py
│   └── twitter.py
├── models/                  # Data models
│   ├── tutorial.py          # Tutorial content model
│   ├── trend.py             # Trend data model
│   ├── score.py             # Quality score model
│   └── topic.py             # Topic taxonomy model
├── delivery/                # Output channels
│   ├── email_digest.py
│   ├── web_dashboard.py
│   ├── api_server.py
│   └── bot_integration.py
├── storage/                 # Data persistence
│   ├── database.py          # PostgreSQL / SQLite
│   ├── cache.py             # Redis caching layer
│   └── vector_store.py      # Embeddings for semantic search
├── llm/                     # LLM integration
│   ├── summarizer.py        # Summarize tutorials
│   ├── classifier.py        # Classify topics and difficulty
│   └── recommender.py       # Personalized recommendations
├── config/                  # Configuration
│   ├── settings.py
│   ├── sources.yaml         # Source definitions and weights
│   └── topics.yaml          # Topic taxonomy
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project metadata
├── Dockerfile               # Container build
├── docker-compose.yml       # Multi-service setup
└── README.md                # Quick start guide
```

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Language** | Python 3.12+ | AI/ML ecosystem, async support, rich libraries |
| **Agent Framework** | Claude Agent SDK / LangGraph | Orchestration of autonomous agent workflows |
| **LLM** | Claude API (Anthropic) | Summarization, classification, recommendations |
| **Web Scraping** | Playwright + BeautifulSoup | Dynamic and static content extraction |
| **Search/Trends** | SerpAPI, Google Trends API | Programmatic access to search data |
| **Database** | PostgreSQL | Structured data, full-text search |
| **Vector Store** | ChromaDB / Pinecone | Semantic similarity for deduplication and recommendations |
| **Cache** | Redis | Rate limiting, response caching, job queues |
| **Task Queue** | Celery / APScheduler | Scheduled crawling and processing |
| **API** | FastAPI | REST API for dashboard and integrations |
| **Frontend** | Next.js or Streamlit | Web dashboard for browsing curated content |
| **Deployment** | Docker + Railway / Fly.io | Containerized, easy to deploy |

---

## Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    TREND      │    │   CONTENT    │    │   QUALITY    │  │
│  │   DETECTOR    │───▶│   CRAWLER    │───▶│   SCORER     │  │
│  │              │    │              │    │              │  │
│  │ • Google     │    │ • YouTube    │    │ • Relevance  │  │
│  │ • Reddit     │    │ • GitHub     │    │ • Freshness  │  │
│  │ • HN         │    │ • Medium     │    │ • Engagement │  │
│  │ • Twitter    │    │ • Blogs      │    │ • Depth      │  │
│  │ • SO         │    │ • Courses    │    │ • Credibility│  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                  │          │
│                                          ┌───────▼───────┐  │
│  ┌──────────────┐                        │   CURATOR &   │  │
│  │     GAP      │◀───────────────────────│   DELIVERY    │  │
│  │   ANALYZER   │                        │               │  │
│  │              │                        │ • Digest      │  │
│  │ • Unmet needs│                        │ • Dashboard   │  │
│  │ • Opportunities│                      │ • API         │  │
│  └──────────────┘                        │ • Bot         │  │
│                                          └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Models

### Tutorial
```python
@dataclass
class Tutorial:
    id: str                    # Unique identifier
    title: str                 # Tutorial title
    url: str                   # Source URL
    source: str                # Platform (youtube, github, medium, etc.)
    author: str                # Creator name
    published_at: datetime     # Publication date
    discovered_at: datetime    # When our agent found it
    topic: str                 # Primary topic
    tags: list[str]            # Related tags
    difficulty: str            # beginner | intermediate | advanced
    content_type: str          # video | article | repo | course | paper
    summary: str               # LLM-generated summary
    engagement: dict           # Views, likes, stars, comments
    quality_score: float       # Composite quality score (0-100)
    trending_score: float      # How trending the topic is (0-100)
    final_rank: float          # Combined ranking score
```

### Trend
```python
@dataclass
class Trend:
    id: str
    topic: str                 # e.g., "MCP servers", "Claude Agent SDK"
    query: str                 # Search query driving the trend
    velocity: float            # Rate of search volume increase
    volume: int                # Current search volume
    sources: list[str]         # Where the trend was detected
    first_seen: datetime       # When trend was first detected
    peak_predicted: datetime   # Estimated peak date
    category: str              # LLM, Vision, Agents, MLOps, etc.
    related_topics: list[str]  # Related trending topics
```

---

## Scoring Algorithm

The composite quality score is calculated as:

```
final_score = (
    w_relevance  * relevance_score  +
    w_freshness  * freshness_score  +
    w_engagement * engagement_score +
    w_depth      * depth_score      +
    w_credibility * credibility_score
) * trend_multiplier
```

Default weights:
- `w_relevance = 0.25`
- `w_freshness = 0.20`
- `w_engagement = 0.20`
- `w_depth = 0.25`
- `w_credibility = 0.10`

The `trend_multiplier` boosts content that matches a currently accelerating trend (1.0–2.0x).

---

## Monetization Model — Free vs Premium

AI Tutorial Hunter uses a **time-delayed freemium** model with three tiers:

### Free Tier ($0) — Capture & Engage
| What's Free | Why |
|-------------|-----|
| Beginner-level tutorials | Low barrier to entry, builds top of funnel |
| Weekly digest (top 3 only) | Taste of quality, drives upgrades |
| Trend overview (titles only) | Hook users with what's hot |
| All content after 7-day delay | Time-delayed freemium — everyone gets it eventually |

### Pro Tier ($9.99/mo) — Power Users
| Feature | Value |
|---------|-------|
| Daily digest (full ranked lists) | Complete intelligence |
| All difficulty levels | Intermediate + Advanced content |
| Real-time trend alerts (<24h old) | Speed advantage |
| Quality scores + deep summaries | Know what's worth your time |
| Personalized recommendations | Tailored learning paths |
| Full search and filter | Find exactly what you need |

### Team Tier ($29.99/mo) — B2B & Creators
| Feature | Value |
|---------|-------|
| Everything in Pro | Full access |
| API access (1000 req/day) | Build integrations |
| Content gap analysis | Identify what to create |
| Historical trend analytics | Strategic planning |
| Slack/Discord integration | Team workflow |
| Priority support | Direct line |

### Classification Logic
```
if difficulty == "beginner"     → FREE  (always — hook new users)
if age > 7 days                 → FREE  (time-delayed freemium)
if recent + high quality        → PREMIUM (speed advantage)
if intermediate/advanced        → PREMIUM (depth value)
```

---

## Roadmap

### Phase 1 — Foundation (Weeks 1–2)
- [ ] Project scaffolding and environment setup
- [ ] Trend Detector agent: Google Trends + Reddit integration
- [ ] Content Crawler agent: YouTube + GitHub discovery
- [ ] Basic quality scoring
- [ ] SQLite storage, CLI output

### Phase 2 — Intelligence (Weeks 3–4)
- [ ] LLM integration for summarization and classification
- [ ] Quality scoring with depth and credibility analysis
- [ ] Add sources: Hacker News, Medium, ArXiv, X/Twitter
- [ ] Vector store for deduplication and semantic search
- [ ] Gap analysis agent

### Phase 3 — Delivery (Weeks 5–6)
- [ ] FastAPI REST endpoint
- [ ] Email digest generation and delivery
- [ ] Web dashboard (Next.js or Streamlit)
- [ ] User preferences and personalization
- [ ] Slack/Discord bot integration

### Phase 4 — Scale & Polish (Weeks 7–8)
- [ ] Scheduled automated runs (Celery/cron)
- [ ] Rate limiting and polite crawling
- [ ] Monitoring and alerting
- [ ] Docker containerization
- [ ] Deployment to production
- [ ] Performance optimization and caching

---

## Configuration

### Environment Variables
```bash
# LLM
ANTHROPIC_API_KEY=sk-ant-...

# Search APIs
SERPAPI_KEY=...
YOUTUBE_API_KEY=...
GITHUB_TOKEN=ghp_...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
TWITTER_BEARER_TOKEN=...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tutorial_hunter
REDIS_URL=redis://localhost:6379

# Delivery
SMTP_HOST=smtp.gmail.com
SMTP_USER=...
SMTP_PASS=...

# App
CRAWL_INTERVAL_HOURS=6
MAX_RESULTS_PER_SOURCE=50
QUALITY_THRESHOLD=60
```

---

## Usage Examples

### CLI
```bash
# Run trend detection
python -m ai_tutorial_hunter detect-trends

# Discover tutorials for a trending topic
python -m ai_tutorial_hunter discover --topic "MCP servers"

# Generate today's digest
python -m ai_tutorial_hunter digest --format email

# Run full pipeline
python -m ai_tutorial_hunter run --all
```

### API
```
GET  /api/trends              # Current trending AI topics
GET  /api/tutorials           # Top-ranked tutorials
GET  /api/tutorials?topic=rag # Filter by topic
GET  /api/digest/today        # Today's curated digest
GET  /api/gaps                # Underserved topics
POST /api/preferences         # Set user preferences
```

---

## License

MIT

---

## Contributing

This project is in active development. See the roadmap above for current priorities.
