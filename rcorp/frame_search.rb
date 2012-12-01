#!/usr/bin/env ruby

require_relative 'corpus'

FILLER = Corpus::ICT_NOTION
FRAME_SCHS = [[Corpus::ICT_FUNC, Corpus::ICT_FUNC, Corpus::ICT_FUNC],
              [Corpus::ICT_FUNC, FILLER, Corpus::ICT_FUNC]]
FRAME_THS = 40.0/1000000

if __FILE__ == $0
    if ARGV.length != 1
        exit
    end
    corpfiles = Corpus::read_corpus ARGV[0]
    words_num = 0
    corpfiles.each do |corpfile|
        words_num += corpfile.word_num
    end
    #corpfiles.each do |corpfile|
    #    puts "#{corpfile.filename} #{corpfile.subsens.length}"
    #end
    frames = Corpus::Frame::get_frames(corpfiles, FILLER, FRAME_SCHS)
    frames = frames.select { |k, frame| frame.ref.size > 5 }
    frames = frames.select { |k, frame| frame.frq >= FRAME_THS*words_num }
    frames.each do |k, frame|
        puts "Frame: #{k}, Frq: #{frame.frq}, in #{frame.ref.size} files"
        #frame.ref.each do |file, opts|
        #    puts "\tIn file #{file}:"
        #    puts "\t\t#{opts}"
        #end
    end
end
