terraform {
  // recommend locking to a tag `ref` (ex. `v1.8.7`) rather than a branch IRL
  // `depth=1` means to do a shallow clone, which is what we want in most cases
  #source = "github.com/wbd-streaming/infra-o11y-grafana//terraform/modules/grafana-irsa?depth=1&ref=1.0.0"
    source = "${get_repo_root()}/v2/infra/terraform/modules//confluent-service-team-update-topic-config"
}

include "root" {
  path           = find_in_parent_folders()
  merge_strategy = "deep"
}