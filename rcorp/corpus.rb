﻿#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
require 'set'

module Corpus

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

    ICT_NOTION = ICT_N | ICT_T | ICT_S | ICT_A | ICT_B | ICT_Z |
        ICT_R | ICT_M | ICT_Q | ICT_D 

    ICT_FUNC = ICT_F | ICT_P | ICT_C | ICT_U | ICT_E | ICT_Y | ICT_O 
	

    FILE_TYPE = '.out'
    POS_SEP   = '/'

    class Word

        attr_reader :word, :tag

        def initialize(text)
            tmp = text.split(POS_SEP)
            @word = tmp[0]
            if tmp[1]
                @tag = tmp[1].to_sym
            else
                @tag = :UNKNOWN
            end
        end

        def is_punc?
            return ICT_PUNC.member? @tag
        end

        def to_s
            return @word
        end

    end

    class CorpFile

        attr_reader :filename
        def initialize(filename)
            @filename = filename
            f = File.open filename, encoding: Encoding::UTF_8
            @text = f.read
            #puts @text
            #exit
        end

        def words
            return @words if @words
            @words = (@text.split(/\s/).reject { |text| text.empty? })
                .collect { |text| Word.new text }
        end

        # Output: array of array of words,
        # each array of words is a sub sentence, without punction
        def subsens
            return @subsens if @subsens
            @subsens = Array.new
            tmp = Array.new
            words.each do |word|
                if word.is_punc?
                    if not tmp.empty?
                        @subsens << tmp
                        tmp = Array.new
                    end
                else
                    tmp << word
                end
            end
            return @subsens
        end

        def punc_num
            return @punc_num if @punc_num
            @punc_num = words.count { |word| ICT_PUNC.include? word.tag  }
        end

        def word_num
            return @word_num if @word_num
            @word_num = words.length - punc_num
        end

    end

    class Frame

        @@filler = ICT_NOTION
        #FRAME_SCH = [[FUNC, FUNC, FUNC, FUNC], [FUNC, NOTION, FUNC, FUNC],
        #    [FUNC, FUNC, NOTION, FUNC]]
        @@frame_schs = [[ICT_FUNC, ICT_FUNC, ICT_FUNC],
            [ICT_FUNC, @@filler, ICT_FUNC]]

        attr_reader :words, :type, :ref, :frq

        def initialize(words, type, filename)
            @words = words
            @type = type
            @ref = Hash.new
            @ref[filename] = Hash.new
            @frq = 1
            @@frame_schs[@type].each_with_index do |pos_type, index|
                @ref[filename][@words[index].word] = 1 if pos_type == @@filler
            end
        end

        def self.is_frame?(words, framesch)
            return false if words.length != framesch.length
            framesch.each_with_index do |type, index|
                return false unless type.include? words[index].tag
            end
            return true
        end
        
        def to_sym
            return name.to_sym
        end

        def name
            ret = ''
            @@frame_schs[@type].each_with_index do |pos_type, index|
                if pos_type != @@filler
                    ret << @words[index].word
                else
                    ret << '*'
                end
                ret << ' '
            end
            return ret
        end

        def self.get_frames(corpfiles, filler, frame_schs)
            frames = Array.new
            tmp = Array.new
            @@filler = filler
            @@frame_schs = frame_schs
            corpfiles.each do |corpfile|
                corpfile.subsens.each do |subsen|
                    @@frame_schs.each_with_index do |framesch, findex|
                        0.upto(subsen.length-framesch.length-1).each_with_index do |sindex|
                            0.upto(framesch.length-1) { |i| tmp << subsen[sindex+i] }
                            frames << Frame.new(tmp, findex, corpfile.filename) if is_frame? tmp, framesch 
                            tmp = Array.new
                        end
                    end
                end
            end
            # Merge frames
            frame_hash = Hash.new nil
            frames.each do |frame|
                if frame_hash[frame.to_sym]
                    frame_hash[frame.to_sym].merge frame
                else
                    frame_hash[frame.to_sym] = frame
                end
            end
            return frame_hash
        end

        def merge(other_frame)
            other_frame.ref.each do |filename, opts|
                if @ref[filename]
                    opts.each do |opt, frq|
                        if @ref[filename][opt]
                            @ref[filename][opt] += frq
                        else
                            @ref[filename][opt] = frq
                        end
                    end
                else
                    @ref[filename] = opts
                end
            end
            @frq += other_frame.frq
        end

        def has_char?(sepc_chars)
            sepc_chars.each do |char|
                return true if name.include? char
            end
            return false
        end

    end

    def self.read_corpus(dir)
        ret = Array.new
        Dir.glob("#{dir}/*").each_with_object({}) do |f, h|
            if File.file? f and File.basename(f).end_with? FILE_TYPE
                ret << (CorpFile.new f)
            elsif File.directory? f
                ret += read_corpus f
            end
        end
        return ret
    end

end


