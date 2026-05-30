ARG UPSTREAM
ARG RUNTIME

FROM ${UPSTREAM} AS build

ARG GO_VERSION
COPY . /src
WORKDIR /src

RUN ansible-galaxy install -r requirements.yml \
 && ansible-playbook playbook.yml -e go_version=${GO_VERSION} \
 && rm -rf /src

FROM ${RUNTIME}
LABEL org.opencontainers.image.authors="wagner.bradford@gmail.com"
COPY --from=build /usr/local /usr/local
