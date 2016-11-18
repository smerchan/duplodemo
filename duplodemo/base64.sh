#!/usr/bin/env bash
echo #!/usr/bin/env bash >> /etc/profile.d/duplo.sh
echo export SQLSERVER=duplodb.camivdvpmjvy.us-east-1.rds.amazonaws.com >> /etc/profile.d/duplo.sh
echo export SQLUSER=duplo >> /etc/profile.d/duplo.sh
echo export SQLPASSWD=duplo123 >> /etc/profile.d/duplo.sh
echo export SQLDB=duplo >> /etc/profile.d/duplo.sh

