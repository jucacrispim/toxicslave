#!/bin/bash

pylint toxicslave/
if [ $? != "0" ]
then
    exit 1;
fi

flake8 toxicslave/

if [ $? != "0" ]
then
    exit 1;
fi

flake8 tests
exit $?;
