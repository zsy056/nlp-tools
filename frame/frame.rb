#!/usr/bin/env ruby
require 'set'

module Frame

    ICT_PUNC = Set[:w, :wkz, :wky, :wyz, :wyy, :wj, :ww, :wt, :wd,
        :wf, :wn, :wm, :ws, :wp, :wb, :wh]
    
    ICT_N = Set[:n, :nr, :nr1, :nr2, :nrj, :nrf, :ns, :nsf, :nt,
        :nz, :nl, :ng]

    ICT_T = Set[:t, :tg]

    ICT_S = Set[:s]

    ICT_V = Set[:v, :vd, :vn, :vshi, :vyou, :vf, :vx, :vi, :vl,
        :vg]

    ICT_A = Set[:a, :ad, :an, :ag, :al]

    ICT_B = Set[:b, :bl]

    ICT_Z = Set[:z]

    ICT_R = Set[:r, :rr, :rz, :rzt, :rzs, :rzv, :ry, :ryt, :rys, :ryy, :rg]

    ICT_M = Set[:m, :mq]

    ICT_Q = Set[:q, :qv, :qt]

    ICT_D = Set[:d]

    ICT_F = Set[:f]

    ICT_P = Set[:p, :pba, :pbei]

    ICT_C = Set[:c, :cc]

    ICT_U = Set[:u, :uzhe, :ule, :uguo, :ude1, :ude2, :ude3, :usuo, :udeng,
        :uyy, :udh, :uls, :uzhi, :ulian]

    ICT_E = Set[:e]

    ICT_Y = Set[:y]

    ICT_O = Set[:o]

    ICT_NOTION = ICT_N | ICT_T | ICT_S | ICT_V | ICT_A | ICT_B | ICT_Z |
        ICT_R | ICT_M | ICT_Q | ICT_D

    ICT_FUNC = ICT_F | ICT_P | ICT_C | ICT_U | ICT_E | ICT_Y | ICT_O

    FILE_TYPE = '.out'
    POS_SEP   = '/'

    NOTION = 0
    FUNC   = 1
    PUNC   = 2

    FRAME_LENGTH = 3

    #FRAME_SCH = [[FUNC, FUNC, FUNC, FUNC], [FUNC, NOTION, FUNC, FUNC],
    #    [FUNC, FUNC, NOTION, FUNC]]
    FRAME_SCH = [[FUNC, FUNC, FUNC], [FUNC, NOTION, FUNC]]
    NOT_FRAME = -1

    FRAME_THS = 40.0/1000000

    class Word

        attr_reader :word

        def initialize(text)
            tmp = text.split(POS_SEP)
            @word = tmp[0]
            if tmp[1]
                @tag = tmp[1].to_sym
            else
                @tag = :UNKNOWN
            end
        end

        def is_func?
            return ICT_FUNC.member? @tag
        end

        def is_notion?
            return ICT_NOTION.member? @tag
        end

        def is_punc?
            return ICT_PUNC.member? @tag
        end

        def to_s
            return @word
        end

    end

    # Input: array of word
    # Output: array of array of words,
    # each array of words is a sub sentence, without punction
    def self.get_sub_sen(words)
        ret = []
        tmp = []
        words.each do |word|
            if word.is_punc?
                if not tmp.empty?
                    ret << (Marshal::load Marshal::dump tmp)
                    tmp.clear
                end
            else
                tmp << word
            end
        end
        return ret
    end

    def self.get_words(itext)
        texts = itext.split /\s/
        texts = texts.reject { |text| text.empty? }
        return texts.collect { |text| Word.new text }
    end

    class Frame

        attr_reader :words, :type, :opt, :frq

        def initialize(words, type)
            @words = words
            @type = type
            @opt = []
            @frq = 1
            FRAME_SCH[@type].each_with_index do |pos_type, index|
                @opt << @words[index].word if pos_type == NOTION
            end
        end

        def self.frame_type(words)
            return NOT_FRAME if words.length != FRAME_LENGTH
            FRAME_SCH.each_with_index do |sch, sindex|
                flag = true
                sch.each_with_index do |type, index|
                    case type
                    when NOTION then
                        unless words[index].is_notion?
                            flag = false
                            break
                        end
                    when FUNC   then
                        unless words[index].is_func?
                            flag = false
                            break
                        end
                    end
                end
                return sindex if flag 
            end
            return NOT_FRAME
        end
        
        def to_sym
            return to_s.to_sym
        end

        def to_s
            ret = ''
            FRAME_SCH[@type].each_with_index do |pos_type, index|
                if pos_type == FUNC
                    ret << @words[index].word
                else
                    ret << '*'
                end
                ret << ' '
            end
            return ret
        end

        def self.get_frames(text)
            subsens = ::Frame::get_sub_sen ::Frame::get_words text
            frames = []
            # Get initial frames
            subsens.each do |subsen|
                tmp = []
                subsen[0..-FRAME_LENGTH].each_with_index do |word, index|
                    0.upto(FRAME_LENGTH-1) { |i| tmp << subsen[index+i] }
                    type = frame_type tmp
                    frames << Frame.new(tmp, type) if type != NOT_FRAME
                end
            end
            # Merge frames
            frame_hash = Hash.new(nil)
            frames.each do |frame|
                if frame_hash[frame.to_sym]
                    frame_hash[frame.to_sym].merge frame
                else
                    frame_hash[frame.to_sym] = frame
                end
            end
            # Select frame with frq more than threshold 
            thres =  FRAME_THS * (::Frame::count_words text)
            return frame_hash.select { |k, v| v.frq > thres } 
        end

        def merge(other_frame)
            @opt.concat other_frame.opt
            @frq += other_frame.frq
        end
    end

    def self.read_corpus(dir)
        ret = ''
        Dir.glob("#{dir}/*").each_with_object({}) do |f, h|
            if File.file? f and File.basename(f).end_with? FILE_TYPE
                ret += IO.read f
            elsif File.directory? f
                ret += read_corpus f
            end
        end
        return ret
    end

    def self.count_sep(text)
        return text.count POS_SEP
    end

    def self.count_punc(text)
        ret = ICT_PUNC.inject(0) do |ret, punc|
            ret += text.scan(punc.to_s).length
        end
        return ret
    end

    def self.count_words(text)
        return (count_sep text) - (count_punc text) 
    end

end

if __FILE__ == $0
    Frame::Frame::get_frames(Frame::read_corpus ARGV[0]).each do |k, frame|
        puts "Frame: #{frame.to_s}, Frq: #{frame.frq}"
        #puts frame.opt.to_s
    end
end
