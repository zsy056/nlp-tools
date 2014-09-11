#!/usr/bin/env ruby
# -*- coding: utf-8 -*-

require_relative 'corpus'

# Configs
load 'config.txt'

if __FILE__ == $0
    corpfiles = Corpus::read_corpus INPUT
    words_num = 0
    corpfiles.each do |corpfile|
        words_num += corpfile.word_num
    end
    #corpfiles.each do |corpfile|
    #    puts "#{corpfile.filename} #{corpfile.subsens.length}"
    #end
    frames = Corpus::Frame::get_frames(corpfiles, FILLER, FRAME_SCHS)
    frames = frames.select { |k, frame| frame.ref.size >= FILE_THS }
    frames = frames.select { |k, frame| frame.frq >= FRAME_THS*words_num }
    frames = frames.select { |k, frame| frame.has_char? SPEC_CHARS } unless SPEC_CHARS.empty?
    File.open(OUTPUT, 'w') do |f|
        f.puts "Found #{frames.size} frames."
        frames.each do |k, frame|
            f.puts "Frame: #{k}, Frq: #{frame.frq}, in #{frame.ref.size} files"
            frame.ref.each do |file, opts|
                f.puts "\tIn file #{file}:"
                opts.each do |opt, frq|
                    f.puts "\t\tOPT: #{opt}, Frq: #{frq}"
                end
            end
        end
    end
end
