require 'json'

module Jekyll
  class FoodtruckPageGenerator < Generator
    safe true
    priority :normal

    def generate(site)
      items = load_json(site, '_rawdata/foodtruck.json')
      Jekyll.logger.info "FoodtruckGenerator:", "#{items.size}개 푸드트럭허가구역 페이지 생성 중..."
      items.each do |z|
        next if z['slug'].to_s.strip.empty?
        site.pages << FoodtruckPage.new(site, z)
      end
      Jekyll.logger.info "FoodtruckGenerator:", "완료 (#{items.size}개)"
    end

    private

    def load_json(site, path)
      file = File.join(site.source, path)
      return [] unless File.exist?(file)
      JSON.parse(File.read(file, encoding: 'utf-8'))
    rescue => e
      Jekyll.logger.warn "FoodtruckGenerator:", "#{path} 로드 실패: #{e.message}"
      []
    end
  end

  class FoodtruckPage < Page
    def initialize(site, z)
      @site = site
      @base = site.source
      @dir  = "foodtruck/#{z['slug']}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'foodtruck.html')
      self.data.merge!(z)
      self.data['layout']      = 'foodtruck'
      self.data['title']       = build_title(z)
      self.data['description'] = build_desc(z)
    end

    private

    def build_title(z)
      loc = [z['doShort'], z['sigungu']].compact.join(' ')
      "#{z['zoneName']} 푸드트럭 허가구역 #{loc} 위치·운영시간"
    end

    def build_desc(z)
      loc = [z['doShort'], z['sigungu']].compact.join(' ')
      "#{loc} #{z['zoneName']} 푸드트럭 허가구역. 운영대수 #{z['vehicleCount']}대, 위치와 운영시간을 확인하세요."[0, 155]
    end
  end
end
