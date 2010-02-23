require 'rubygems'
require 'sinatra'
require 'mongo'
require 'json' 
require 'dm-core'
require 'mongo_adapter'

DataMapper.setup(:default, :adapter => 'mongo', :database => 'shepherd')

class Repository
  include DataMapper::Mongo::Resource

  property :id, ObjectID
  property :tags, Array
end

class Package
  include DataMapper::Mongo::Resource

  property :id, ObjectID
  property :filename, String
  property :creation_date, Date
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
 
json_get '/' do
  'Hello'
end

get '/repos/:id' do
  id = params[:id]
  {:tags => Repository.get(id).tags}.to_json
end