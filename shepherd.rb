require 'rubygems'
require 'sinatra'
require 'mongo'
require 'json' 
require 'dm-core'
require 'mongo_adapter'
require 'base64'
require 'time'

DataMapper.setup(:default, :adapter => 'mongo', :database => "shepherd#{rand(1002000)}")


class Repository
  include DataMapper::Mongo::Resource

  property :id, ObjectID
  property :tags, Array
end

class Package
  include DataMapper::Mongo::Resource

  property :id, ObjectID
  property :filename, String, :required => true
  property :data, String, :required => true
  property :tags, Array
end

configure :production do
  enable :raise_errors
end

def json_get(route, options={}, &block)
  get(route, options) do 
    block.call.to_json
  end
end

before do
  content_type 'application/json'
end

json_get '/' do
  'Hello'
end

get '/repos/:id' do
  repo = Repository.get(params[:id])
  raise Sinatra::NotFound if repo.nil?
  {:tags => repo.tags}.to_json
end

delete '/repos/:id' do
  Repository.get(params[:id]).destroy!
  {:message => "Repository deleted"}.to_json
end


get '/repos/:id/:filename' do
  repo = Repository.get(params[:id])
  raise NotFound if repo.nil?

  p = Package.first(:tags => repo.tags, :filename => params[:filename])
  raise NotFound if p.nil?
  Base64.decode64 p.data
end