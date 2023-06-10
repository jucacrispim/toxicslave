Build docker images
===================

The image that will be used in a build - if docker enabled in the slave - is based
in the parameter ``platform`` passed by the master to the slave.

The master select the platform by:

1) Using the platform param in a builder

2) Concatenating the language param with its versions. If the config
   has docker = true, the platform will have the prefix ``docker-``
