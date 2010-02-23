require File.dirname(__FILE__) + '/spec_helper'

describe "Shepherd" do
  include Rack::Test::Methods

  def app
    @app ||= Sinatra::Application
  end

  context 'repository' do
    before(:all) do
      @tags = {'tags' => ['esn-tools', 'website-dev']}
      @repo = Repository.create(@tags)
      @nginx = Package.create(:filename => 'nginx-0.8.33-3.el5.x86_64.rpm', :tags => ['esn-tools'])
    end
    
    it "provides meta data about itself" do
      # TODO: Check content type
      get "/repos/#{@repo.id}"
      JSON.parse(last_response.body).should == @tags
    end

    it "serves packages with matching tags" do
      get "/#{@repo.id}/#{@nginx.filename}"
      last_response.should be_ok
    end
  end
end