Migrating openstack keystone from v2 to v3
Steps to configure Keystone:
Update Keystone Endpoint:
      $ mysql
          mysql> use keystone;
         mysql> select interface, url from endpoint e, service s where s.id=e.service_id and s.type="identity";
         +-----------+-----------------------------+
         | interface | url                    	 |
         +-----------+-----------------------------+
         | internal  | http://127.0.0.1:5000/v2.0  |
         | public    | http://127.0.0.1:5000/v2.0  |
         | admin     | http://127.0.0.1:35357/v2.0 |
         +-----------+-----------------------------+
         3 rows in set (0.00 sec)
        Now, update all three URLs, change V2.0 API to V3 with:
        mysql> select id from service where type="identity";
       +----------------------------------+
       | id                          	 |
       +----------------------------------+
       | b0bbb0370ee4402eb3770129fdc0c328 |
       +----------------------------------+
       1 row in set (0.00 sec)
      mysql> update endpoint set url="http://127.0.0.1:5000/v3" where url="http://127.0.0.1:5000/v2.0" and                                                                                               service_id="b0bbb0370ee4402eb3770129fdc0c328";
      mysql> update endpoint set url="http://127.0.0.1:35357/v3" where url="http://127.0.0.1:35357/v2.0" and service_id="b0bbb0370ee4402eb3770129fdc0c328";
Confirm that you have all three endpoints updated to V3:
mysql> select interface, url from endpoint e, service s where s.id=e.service_id and s.type="identity";
    +-----------+---------------------------+
    | interface | url                  	 |
    +-----------+---------------------------+
    | internal  | http://127.0.0.1:5000/v3  |
    | public    | http://127.0.0.1:5000/v3  |
    | admin     | http://127.0.0.1:35357/v3 |
    +-----------+---------------------------+
    3 rows in set (0.00 sec)
2) Update Policy.json
Change /etc/keystone policy.json
mv /etc/keystone/policy.json /etc/keystone/policy.json.bckup
cp /opt/stack/keystone/etc/policy.v3cloudsample.json ->  /etc/keystone/policy.json
Change /opt/stack/horizon/openstack_dashboard/conf/keystone_policy.json
 mv /opt/stack/horizon/openstack_dashboard/conf/keystone_policy.json{,.bckup}
 cp  /opt/stack/keystone/etc/policy.v3cloudsample.json -> 
       /opt/stack/horizon/openstack_dashboard/conf/keystone_policy.json
      Change policy.json line3:
      “cloud_admin”: “rule:admin_required and domain_id: admin_default_id”
       to  “cloud_admin”: “rule:admin_required”  for project-level authorization  scope.
       or,
       to “cloud_admin”: “rule:admin_required and domain_id: <admin_default_id>” 
        for domain-level authorization    scope 
       Change /opt/stack/horizon/openstack_dashboard/conf/keystone_policy.json
       "cloud_admin": "role:admin and (token.is_admin_project:True or domain_id:admin_domain_id)",
     To
     "cloud_admin": "role:admin and (is_admin_project:True or domain_id:admin_domain_id)",
3) check [keystone_authtoken] section in neutron.conf, nova.conf, glance-api.conf, glance-registry.conf, cinder.conf and other services configuration with this section to
have :
                       Auth_uri = http:<ip address>:5000/v3
                 Auth_url = http:<ip_address>:35357/v3
                                          or 
                      Auth_uri = http:<ip address>:5000
                      Auth_url = http:<ip_address>:35357
                      Auth_version = v3
Now restart all the services.
Verify:
Run command openstack project list --debug , 
Request should use v3 url to fetch auth_token.
Source file:
    Export OS_USERNAME=admin
    Export OS_PASSWORD=mysecret
    Export OS_AUTH_URL=http://<ip_address>:5000/v3
    Export OS_PROJECT_NAME=admin
    Export OS_REGION_NAME=RegionOne
    Export SERVICE_TOKEN=admin
    Export OS_PROJECT_DOMAIN_NAME=default
    Export OS_USER_DOMAIN_NAME=default
    Export SERVICE_ENDPOINT=http://<ip_address>:5000/v3
    Export OS_IDENTITY_API_VERSION=3
Server Authentication using self signed certificates:
Create a self signed certificate for the server:
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/apache-selfsigned.key -out /etc/ssl/certs/apache-selfsigned.crt
While creating the openssl certificate give common name your <hostname> or <ip_address> .
 If you want to use <hostname> then set your ip_address with hostname in  /etc/hosts.
you can get hostname by running command: hostname
      Note: All below steps are based on certificate with common name passed as
                <hostname>, if you want to use <ip_address> please use <ip_address>
                wherever <hostname> is used.
Configure Apache:
Configure /etc/apache2/sites-enabled/keystone.conf
                 <VirtualHost *:5000>
                     ****
                     SSLEngine on
                     SSLCertificateKeyFile /etc/ssl/private/apache-selfsigned.key
                     SSLCertificateFile /etc/ssl/certs/apache-selfsigned.crt
                     ****
                 </VirtualHost>
                 <VirtualHost *:35357>
                     ****
                     SSLEngine on
                     SSLCertificateKeyFile /etc/ssl/private/apache-selfsigned.key
                     SSLCertificateFile /etc/ssl/certs/apache-selfsigned.crt
                     ****
                 </VirtualHost>
3) Update Keystone Endpoint:
      $ mysql
          mysql> use keystone;
         mysql> select interface, url from endpoint e, service s where s.id=e.service_id and s.type="identity";
         +-----------+-----------------------------+
         | interface | url                    	 |
         +-----------+-----------------------------+
         | internal  | http://hostname:5000/v3  |
         | public    | http://hostname:5000/v3  |
         | admin     | http://hostname:35357/v3 |
         +-----------+-----------------------------+
         3 rows in set (0.00 sec)
        Now, update all three URLs, change http to https with:
        mysql> select id from service where type="identity";
       +----------------------------------+
       | id                          	 |
       +----------------------------------+
       | b0bbb0370ee4402eb3770129fdc0c328 |
       +----------------------------------+
       1 row in set (0.00 sec)
      mysql> update endpoint set url="https://hostname:5000/v3" where url="http://<hostname>:5000/v3" and                                                                                               service_id="b0bbb0370ee4402eb3770129fdc0c328";
      mysql> update endpoint set url="https://hostname:35357/v3" where url="http://<hostname>:35357/v3" and service_id="b0bbb0370ee4402eb3770129fdc0c328";
Confirm that you have all three endpoints updated to Https:
mysql> select interface, url from endpoint e, service s where s.id=e.service_id and s.type="identity";
    +-----------+---------------------------------+
    | interface | url                  	                     |
    +-----------+---------------------------------+
    | internal  | https://hostname:5000/v3|
    | public    | https://hostname:5000/v3  |
    | admin     | https://hostname:35357/v3|
    +-----------+----------------------------------+
    3 rows in set (0.00 sec)
4) Change keystone.conf
                      admin_endpoint = https://hostname:35357
                              Public_endpoint = https://hostname:5000
5) Configure [Keystone_autoken] section for https auth_url and auth_uri in neutron.conf,
    Nova.conf, glance-api.conf, glance-registry.conf, cinder.conf and other service configuration
    File with this section to have:
                       auth_uri = https://hostname:5000/v3
                 auth_url = https://hostname:35357/v3
                                          or 
                      auth_uri = https://hostname:5000
                      auth_url = https://hostname:35357
                      auth_version = v3
6) Configure [Keystone_authtoken] section in neutron.conf, nova.conf,glance-api.conf,
          Glance-registry.conf, cinder.conf and other services configuration with this section to
          Have:
                       cafile = /etc/ssl/certs/apache-selfsigned.crt
7) Configure neutron.conf [nova] section and nova.conf [neutron] section to have:
                       cafile = /etc/ssl/certs/apache-selfsigned.crt
                               auth_uri = https://hostname:5000/v3
                      auth_url = https://hostname:35357/v3
      For Ocata Openstack:
Configure nova.conf [placement] section to have:
                        cafile = /etc/ssl/certs/apache-selfsigned.crt
                        auth_uri = https://hostname:5000/v3
                        auth_url = https://hostname:35357/v3
8) Changes in /opt/stack/horizon/openstack_dashboard/local/local_settings.py
                      OPENSTACK_KEYSTONE_URL = “https://<hostname>:5000/v3”
                                 OPENSTACK_SSL_CACERT = “/etc/ssl/certs/apache-selfsigned.crt”
                                 OPENSTACK_API_VERSION={“identity”:3}
9) Restart all the services - apache2 , neutron services, glance services, nova services, etc
Verify:
Run command openstack project list --debug and check if it is getting auth_token using
Https request.
Troubleshoot:
If while restarting apache2 server raises exception “Invalid command ‘SSLEngine’”:
Run this command: sudo a2enmod ssl

