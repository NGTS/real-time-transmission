from glob import iglob
from fabric.api import *

env.hosts = ['par-ds']
env.use_ssh_config = True


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


@task
def deploy(branch='master'):
    puts('Deploying branch %s' % branch)
    local('git push origin {branch}'.format(branch=branch))
    with cd('~/srw/real-time-transmission'):
        run('git fetch origin')
        run('git checkout .')
        run('git merge --ff origin/{branch}'.format(branch=branch))
