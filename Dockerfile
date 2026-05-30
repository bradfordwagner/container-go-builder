ARG UPSTREAM
FROM ${UPSTREAM} AS base

ARG GO_VERSION
COPY . /src
WORKDIR /src

RUN ansible-galaxy install -r requirements.yml \
 && ansible-playbook playbook.yml -e go_version=${GO_VERSION} \
 && rm -rf /src
