FROM martinsolie/mcduck-test-base

COPY . /app
WORKDIR /app
RUN chmod +x /app/.ci/test.entrypoint.sh

ENTRYPOINT /app/.ci/test.entrypoint.sh
