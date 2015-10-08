from glob import iglob
from fabric.api import *


@task
def test():
    test_shell()
    test_python()


@task
def test_python():
    local('py.test testing')


@task
def test_shell():
    files = iglob('testing/*.sh')
    for filename in files:
        puts('Testing file %s' % filename)
        local('bash %s' % filename)
