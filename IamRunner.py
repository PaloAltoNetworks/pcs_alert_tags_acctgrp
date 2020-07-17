import lib
import json
import datetime

#---Configuration options
tmconfig = {
    # Data Timerange
    'timerange_unit': 'hour', # day, week, month, hour
    'timerange_amount': 6
    }

    # Enable this to fetch alerts all time
            #'timeRange': {
            #    'type': 'to_now',
            #    'value': 'epoch'
            #}

class AlertExport():
    def __init__(self):
        self.config = lib.ConfigReader()
        self.csv_writer = lib.CsvWriters()
        self.rl_sess = lib.RLSession(self.config.rl_user, self.config.rl_pass, self.config.rl_cust, self.config.rl_api_base)
        self.output = [[
                        "Alert ID", "Policy Name","Policy Type","Description","Policy Labels","Policy Severity","Resource Name","Cloud Type",
                        "Cloud Account Id","Cloud Account Name","Region","Recommendation","Alert Status","Rating","Alert Time","Event Occurred",
                        "Dismissed On","Dismissed By","Dismissal Reason","Resolved On","Resolution Reason","Resource ID", "Tags", "Account groups"
                      ]]
        self.rrn_cache = {}

    def get_cloud_accts(self):
        self.url = "https://" + self.config.rl_api_base + "/cloud"
        self.rl_sess.authenticate_client()
        cloud_accts = self.rl_sess.client.get(self.url)
        cloud_accts_json = cloud_accts.json()
        return cloud_accts_json

    def get_tags(self,rrn):
        if not self.rrn_cache:
            data = json.dumps({ 'rrn': rrn })
            self.url = "https://" + self.config.rl_api_base + "/resource"
            self.rl_sess.authenticate_client()
            resource = self.rl_sess.client.post(self.url,data)
            resource_json = resource.json()
            temp = {rrn: resource_json['tags']}
            self.rrn_cache.update(temp)
        elif rrn in self.rrn_cache:
            for resource_num in self.rrn_cache:
                if resource_num == rrn:
                    return self.rrn_cache[resource_num]
        else:
            data = json.dumps({ 'rrn': rrn })
            self.url = "https://" + self.config.rl_api_base + "/resource"
            self.rl_sess.authenticate_client()
            resource = self.rl_sess.client.post(self.url,data)
            resource_json = resource.json()
            temp = {rrn: resource_json['tags']}
            self.rrn_cache.update(temp)

        return resource_json['tags']

    def get_policies(self):
        self.url = "https://" + self.config.rl_api_base + "/v2/policy"
        self.rl_sess.authenticate_client()
        policies = self.rl_sess.client.get(self.url)
        return policies.json()


    def getalerts(self):
        cloud_accounts = self.get_cloud_accts()
        print("Pulling all Cloud Accounts")
        filters = [{'name': 'alert.status', 'value': 'open', 'operator': '='},{'operator':'=','name':'resource.type','value':'AWS IAM User Managed Policy'},{'operator':'=','name':'resource.type','value':'AWS IAM User Inline Policy'}]
        policies = self.get_policies()
        print("Pulling all Policies")
        blank = '' #needed to handle cases where we don't have data for specific fields in the CSV (only handling open alerts)
        data = json.dumps({
            'detailed': False,
            'filters': filters,
            'timeRange': {
                'type': 'relative',# 'type': 'to_now'
                'value': { # 'value': 'epoch'
                    'amount': tmconfig['timerange_amount'],
                    'unit': tmconfig['timerange_unit']
                }
            }
        })
        self.url = "https://" + self.config.rl_api_base + "/v2/alert"
        self.rl_sess.authenticate_client()
        print("Pulling all Alert data")
        alerts = self.rl_sess.client.post(self.url,data)
        alerts_json = alerts.json()
        for alert in alerts_json['items']:
            acctgrp_names = [] #this is here to clear out the list on each loop to ensure we capture the correct set of account group names for each alert
            stored_policy = {}
            for policy in policies:
                if alert['policy']['policyId'] == policy['policyId']:
                    stored_policy = policy
            if 'rrn' in alert['resource']:
                tags_data = self.get_tags(alert['resource']['rrn'])
            else:
                tags_data = '' # in case tags are not present
            for acct in cloud_accounts: #handles looping through the cloud account data to extract certain needed fields
                if alert['resource']['accountId'] == acct['accountId']:
                    acctname = acct['name']
                    for name in acct['groups']:
                        acctgrp_names.append(name['name'])

            if alert.get('eventOccurred') == None: #need to handle alerts that don't have eventOccurred key
                eventOccurred_date = 'NA'
            else:
                eventOccurred_date = datetime.datetime.fromtimestamp(alert['eventOccurred']/1000.).strftime('%Y-%m-%d %H:%M:%S')
            #### convert policy data into data without brackets and single quotes
            #### this also handles issue if policy isn't available for an alert
            s = ", "
            labels = stored_policy.get("labels","NA")
            if labels != "NA":
                labels = s.join(labels)

            csvdata = [alert["id"], stored_policy.get("name","NA"), stored_policy.get("policyType","NA"), stored_policy.get("description","NA"),
                    labels, stored_policy.get("severity","NA"), alert["resource"]["name"], alert["resource"]["cloudType"],
                    alert["resource"]["accountId"], acctname, stored_policy.get("recommendation","NA"),
                    alert["status"], alert["riskDetail"]["rating"], datetime.datetime.fromtimestamp(alert["alertTime"]/1000.).strftime('%Y-%m-%d %H:%M:%S'),
                    eventOccurred_date, blank, blank, blank, blank, blank, alert["resource"]["id"], str(tags_data)[1:-1], str(acctgrp_names)[1:-1]]

            self.csv_writer.append([csvdata])

    def build(self):
        #write out the top of csv to file
        self.csv_writer.write(self.output)


    def run(self):
        self.build()
        self.getalerts()

def main():
    pc_alertexport = AlertExport()
    pc_alertexport.run()


if __name__ == "__main__":
    main()
