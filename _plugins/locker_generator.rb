require 'json'

module Jekyll
  class LockerPageGenerator < Generator
    safe true
    priority :normal

    def generate(site)
      items = load_json(site, '_rawdata/locker.json')
      Jekyll.logger.info "LockerGenerator:", "#{items.size}개 안심택배함 페이지 생성 중..."
      items.each do |l|
        next if l['slug'].to_s.strip.empty?
        site.pages << LockerPage.new(site, l)
      end
      Jekyll.logger.info "LockerGenerator:", "완료 (#{items.size}개)"
    end

    private

    def load_json(site, path)
      file = File.join(site.source, path)
      return [] unless File.exist?(file)
      JSON.parse(File.read(file, encoding: 'utf-8'))
    rescue => e
      Jekyll.logger.warn "LockerGenerator:", "#{path} 로드 실패: #{e.message}"
      []
    end
  end

  class LockerPage < Page
    def initialize(site, l)
      @site = site
      @base = site.source
      @dir  = "locker/#{l['slug']}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'locker.html')
      self.data.merge!(l)
      self.data['layout']      = 'locker'
      self.data['title']       = build_title(l)
      self.data['description'] = build_desc(l)
    end

    private

    def build_title(l)
      loc = [l['doShort'], l['sigungu']].compact.join(' ')
      "#{l['fcltyName']} 안심택배함 #{loc} 위치·이용방법"
    end

    def build_desc(l)
      loc = [l['doShort'], l['sigungu']].compact.join(' ')
      "#{loc} #{l['fcltyName']} 안심택배함. 무인보관함 위치와 무료이용시간, 이용방법을 확인하세요."[0, 155]
    end
  end
end
