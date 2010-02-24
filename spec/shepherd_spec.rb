require File.dirname(__FILE__) + '/spec_helper'

describe "With Shepherd" do
  include Rack::Test::Methods

  def app
    @app ||= Sinatra::Application
  end

  context 'a repository' do
    before(:all) do
      # TODO: Fix multiple tag support, MongoDB adapter for DataMapper has problems with this?
      @tags = {'tags' => ['esn-tools']}
      @repo = Repository.create(@tags)
      @filename = 'nginx-0.8.33-3.el5.x86_64.rpm'
      @contents = "PLACEHOLDER-DATA"
      @nginx = Package.create(:filename => @filename, :data => Base64.encode64(@contents), :tags => ['esn-tools'])
    end

    it "provides meta data about itself" do
      get "/repos/#{@repo.id}"
      JSON.parse(last_response.body).should == @tags
    end

    it "serves packages with matching tags" do
      get "/repos/#{@repo.id}/#{@nginx.filename}"
      last_response.body.should == @contents
    end
  end
end