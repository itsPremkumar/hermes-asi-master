# Dockerfile — HERMES Advanced
# Hermes-native Docker setup — most sandboxed terminal backend (per config.yaml)

FROM python:3.11-slim

# Hermes runs as non-root (official guideline)
RUN useradd -m hermes && mkdir -p /home/hermes/project && chown hermes:hermes /home/hermes/project
WORKDIR /home/hermes/project

# System deps (git for worktrees, curl for skills, jq for JSON parsing per skill guideline: No External Deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy Hermes Advanced project
COPY --chown=hermes:hermes . ./

# Install Hermes Agent (official)
RUN pip install --no-cache-dir hermes-agent

# Hermes config lives at ~/.hermes/ — mount or copy at runtime
# Do NOT bake .env (secrets) into image — pass via env or mount

USER hermes
EXPOSE 8000

# Default: show Hermes help; override with `hermes` or `hermes chat`
CMD ["hermes", "--help"]
