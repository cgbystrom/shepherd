# Shepherd

A repository manager for [yum](http://en.wikipedia.org/wiki/Yellowdog_Updater,_Modified) with support for virtual repos.

Shepherd decouples packages from what repo they belong to. Packages (or RPMs) are merely uploaded and tagged.
So called *virtual repositories* are then created which also have tags. The view of a repository depends on what tags it have assigned.

This useful for having packages pass through different stages in it's life cycle.
Usually a package is deployed through stages like this:
 * Development
 * Staging
 * Production

With Shepherd, you could upload your RPM once and just re-tag it depending on where in the QA process it belongs.


This is right now more of proof-of-concept than anything else. With this simple idea of package and repository decoupling, it has great potential.

Idea for this pretty much borrowed from Red Hat Satellite/[Spacewalk](http://www.redhat.com/spacewalk/).
The downsides of both of these is that neither supports cloud environments since they require non-volatile server instances.
Quite a turndown in times when all cool kids do cloud deployment.

## Getting started

It's simple Ruby project built with Sinatra. gem install required gems and start shepherd.rb

## Authors

- Carl Bystršm <http://www.pedantique.org/>

## License

Open source licensed under MIT (see _LICENSE_ file for details).