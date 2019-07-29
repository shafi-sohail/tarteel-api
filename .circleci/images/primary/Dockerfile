FROM circleci/python:3.6.8

LABEL maintainer="anas@abouallaban.info"

# --- Tarteel Setup ---
RUN echo "Installing Git-Crypt" && \
    git clone https://github.com/AGWA/git-crypt.git /tmp/git-crypt && \
    cd /tmp/git-crypt && make && sudo make install