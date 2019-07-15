FROM lambci/lambda:build-python3.6

LABEL maintainer="anas@abouallaban.info"

WORKDIR /var/task

# Fancy prompt to remind you are in zappashell
RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\] "' >> /root/.bashrc
# Circle CI and Tarteel dependencies
RUN yum install -y tar ca-certificates gzip openssh \
    gcc gcc-c++ kernel-devel make git openssl-devel
# --- Tarteel Setup ---
RUN echo "Setting up virtualenv" && virtualenv tarteel && source tarteel/bin/activate && \
    echo 'source /var/task/tarteel/bin/activate' >> /root/.bashrc && \
    git clone https://github.com/Tarteel-io/tarteel-api.git && \
    cd tarteel-api && \
    echo "Installing dependencies..." && ./install_gitcrypt.sh

CMD ["bash"]