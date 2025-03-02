import json
import os
import yaml


def check_if_omd_service_exists_in_env(omd_service, filename):
    with open(filename, 'r') as environments_yaml_file:
        for line in environments_yaml_file:
            if f"v2/infra/terraform/service-teams/{omd_service}/boltapi/any-any" in line and '#' not in line:
                return True
    return False

def update_environment_yaml_file(omd_service, filename):
    with open(filename, 'a') as environments_yaml_file:
        environments_yaml_file.write(f"""
    - <<: *api-dev
      awsRegionName: us-east-1
      baseDirectory: v2/infra/terraform/service-teams/{omd_service}/boltapi/any-any
      runnerLabel: development""")

def update_service_teams_directory(omd_service, omd_components):
    base_service_dir = f"v2/infra/terraform/service-teams/{omd_service}/boltapi/any-any"

    # Check if base service directory exists, if not create it
    if not os.path.isdir(base_service_dir):
        os.makedirs(base_service_dir, exist_ok=True)

    # Check if terragrunt.hcl exists, if not create it
    if not os.path.isfile(f"{base_service_dir}/terragrunt.hcl"):
        with open(f"{base_service_dir}/terragrunt.hcl", 'w') as terragrunt_hcl:
            terragrunt_hcl.write("""terraform {
  // recommend locking to a tag `ref` (ex. `v1.8.7`) rather than a branch IRL
  // `depth=1` means to do a shallow clone, which is what we want in most cases
  #source = "github.com/wbd-streaming/infra-o11y-grafana//terraform/modules/grafana-irsa?depth=1&ref=1.0.0"
    source = "${get_repo_root()}/v2/infra/terraform/modules//confluent-service-team-update-topic-config"
}

include "root" {
  path           = find_in_parent_folders()
  merge_strategy = "deep"
}""")
    
    # Check if .tfvars exists, if not create it
    if not os.path.isfile(f"{base_service_dir}/dev-us-east-1.tfvars"):
        with open(f"{base_service_dir}/dev-us-east-1.tfvars", 'w') as tfvars_file:
            tfvars_file.write(f"""cluster_type        = "boltapi"
environment         = "dev"
environment_version = 2
omd_subdivision     = "any-any"
aws_region          = "us-east-1\"""")
    
    # Check if topics.yaml file exists, if not create it
    if not os.path.isfile(f"{base_service_dir}/dev-topics.yaml"):
        with open(f"{base_service_dir}/dev-topics.yaml", 'w') as topics_yaml:
            topics_yaml.write(f"topics:")

    # Check if rbac-rules.yaml file exists, if not create it
    if not os.path.isfile(f"{base_service_dir}/dev-rbac-rules.yaml"):
        with open(f"{base_service_dir}/dev-rbac-rules.yaml", 'w') as rbac_rules_yaml:
            rbac_rules_yaml.write(f"rbac-rules:")

    # Check if service account yaml file exists, if not create it
    if os.path.isfile(f"{base_service_dir}/service-account.yaml"):
        with open(f"{base_service_dir}/service_account.yaml", 'r') as service_accounts_yaml:
            service_accounts = yaml.load(service_accounts_yaml, Loader=yaml.SafeLoader)["service-accounts"]
    else:
            service_accounts = []
    
    existing_components = [x['omd_component'] for x in service_accounts]
    service_accounts_to_be_created = [{'omd_service': omd_service, 'omd_component': x} for x in omd_components if x not in existing_components]
    print(service_accounts_to_be_created)
    service_account_file_content = {'service-accounts': service_accounts + service_accounts_to_be_created}
    print(service_account_file_content)
    with open(f"{base_service_dir}/service-account.yaml", 'w') as service_accounts_yaml:
        service_accounts_yaml.write( yaml.dump(service_account_file_content, default_flow_style=True))


# with open(f'issue-parser-result.json', 'r') as input_json_file:
with open(f'{os.environ['HOME']}/issue-parser-result.json', 'r') as input_json_file:
    input_json = json.loads(input_json_file.read())

omd_components = [x.strip() for x in input_json['omd_component_names'].split(',') if x!='']
omd_service = input_json['omd_service_name']
 
for env in input_json['environment']:
    filename = f'confluent_service-teams_{env}_environments.yaml'
    
    if not check_if_omd_service_exists_in_env(omd_service, filename):
        update_environment_yaml_file(omd_service, filename)
        update_service_teams_directory(omd_service, omd_components)
