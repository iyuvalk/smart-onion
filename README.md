# smart-onion
Machine learning and artificial intelligence layer for Security-Onion

# General idea:
The general idea in this project is to build a set of services that will automatically analyse the outputs 
generated by SecurityOnion by using machine learning, anomaly detection and event correlation to detect Cyber
related events. 


# Architecture
The project's architecture is based on the microservices paradigm: <br />
<pre>
<b>+ backend</b> - Contains all the backend services and components
<b>|    |</b>
<b>|    +---+ services</b> - Contains all the background services
<b>|</b>             <b>|</b>
<b>|             +--- alerter</b> - The alerter service is responsible for filtering alerts and aggregating alerts and anomalies into Cyber events
<b>|</b>             <b>|</b>
<b>|             +--- configurator</b> - The configurator service is responsible of allowing the various services to get and set their config as well as configuring the scheduler of the system (Zabbix)
<b>|</b>             <b>|</b>
<b>|             +--- metrics_analyzer</b> - The metrics analyser service should use ML, deep learning, NLP as well as biologically constrained machine learning (nupic) and statistical algorithms to detect anomalies or indications of unexpected behaviour (either human or network or other) and return the probability for an anomaly in a given metric 
<b>|</b>             <b>|</b>
<b>|             +--- metrics_collector</b> - The metrics collector (a.k.a sampler) service is responsible for querying the raw data (from Security Onion's elasticsearch cluster and from helper DB instances if needed) and create metrics and also allow usage of threshold based alerts
<b>|</b>  
<b>+ frontend</b> - Contains all the frontend services responsible for the UX <br />
</pre>

+ Each such service will have its own HTTP listener using the Bottle framework.
+ Each such service will not depend on any of the other services except for the configurator.
+ Each backend service will be developed in Python 3.5.
+ Each frontend service will be developed in NodeJS.
+ Each such service will be responsible ONLY for its task as listed above. 
+ Each service is defined as a GitHub project with issues 


For more resources on this project see this folder in Google drive (contains relevant information about Numenta's nupic library and few VMs that will be needed to get you started):
https://drive.google.com/open?id=1uol2G02WjjUFv614DC3KC6wPoMR6qUZm
