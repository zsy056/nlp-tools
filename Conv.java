import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.poi.hslf.blip.Metafile.Header;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

/**
 * Represent the dependency information
 * 
 * @author zsy
 * 
 */
class Depend {
	private int id;
	private String word1;
	private String pos1;
	private int num1;
	private String word2;
	private String pos2;
	private int num2;
	private String type;

	public Depend(int id, String word1, String pos1, int num1, String word2,
			String pos2, int num2, String type) {
		this.id = id;
		this.word1 = word1;
		this.pos1 = pos1;
		this.num1 = num1;
		this.word2 = word2;
		this.pos2 = pos2;
		this.num2 = num2;
		this.type = type;
	}

	/**
	 * Give the sentence and the dependency information, return a list of Depend
	 * objects.
	 * 
	 * @param sentInfo
	 * @return
	 */
	public static List<Depend> getDepends(String sentInfo, int id) {
		String[] lines = sentInfo.split("\n");
		List<String> depStrings = new ArrayList<>();
		List<String> poslist = new ArrayList<>();
		List<String> wordList = new ArrayList<>();
		Pattern wordPattern = Pattern.compile("[^\\(\\)]+");
		for (String line : lines) {
			if (line.length() <= 1) {
				continue;
			}
			if (line.charAt(0) != ' ') {
				depStrings.add(line);
			} else {
				Matcher m = wordPattern.matcher(line);
				while (m.find()) {
					String[] tmp = m.group().split(" ");
					if (tmp.length <= 1)
						continue;
					poslist.add(tmp[0]);
					wordList.add(tmp[1]);
				}
			}
		}
		Map<Integer, Depend> depMap = new HashMap<>();
		for (String dep : depStrings) {
			if (!dep.contains("("))
				continue;
			// System.out.println(dep);
			String[] tmp = new String[2];
			tmp[0] = dep.substring(0, dep.indexOf("("));
			tmp[1] = dep.substring(dep.indexOf("(") + 1, dep.length());
			String type = tmp[0];
			String[] words = tmp[1].replace(")", "").split(", ");
			String word1 = words[0].substring(0, words[0].lastIndexOf("-"));
			int num1 = Integer.parseInt(words[0].substring(
					words[0].lastIndexOf("-") + 1).replaceAll("'", ""));
			if (num1 - 1 >= poslist.size())
				continue;
			String pos1 = poslist.get(num1 - 1);
			String word2 = words[1].substring(0, words[1].lastIndexOf("-"));
			int num2 = Integer.parseInt(words[1].substring(
					words[1].lastIndexOf("-") + 1).replaceAll("'", ""));
			if (num2 - 1 >= poslist.size())
				continue;
			String pos2 = poslist.get(num2 - 1);
			depMap.put(num2, new Depend(id, word1, pos1, num1, word2, pos2, num2, type));
		}
		List<Depend> list = new ArrayList<>();
		for(int i=0; i<wordList.size(); ++i) {
			Depend depend = depMap.get(i+1);
			if(depend==null) {
				depend = new Depend(id, "", "", 0, wordList.get(i), poslist.get(i), i+1, "");
			}
			list.add(depend);
		}
		return list;
	}

	public void insertToSheet(Sheet sheet, int pos) {
		Row row = sheet.createRow(pos);

		Cell idCell = row.createCell(0);
		idCell.setCellValue(id);

		Cell num1Cell = row.createCell(1);
		num1Cell.setCellValue(num2);

		Cell word1Cell = row.createCell(2);
		word1Cell.setCellValue(word2);

		Cell pos1Cell = row.createCell(3);
		pos1Cell.setCellValue(pos2);

		Cell num2Cell = row.createCell(4);
		num2Cell.setCellValue(num1);

		Cell word2Cell = row.createCell(5);
		word2Cell.setCellValue(word1);

		Cell pos2Cell = row.createCell(6);
		pos2Cell.setCellValue(pos1);

		Cell typeCell = row.createCell(7);
		typeCell.setCellValue(type);
	}
}

/**
 * Convert The Penn treebank file to an xlsx dependency file
 * 
 * @author zsy
 * 
 */
public class Conv {

	public static void fillWorkbook(Workbook wb, List<Depend> list) {
		Sheet sheet = wb.createSheet();
		// header
		Row header = sheet.createRow(0);
		// 句子编号 句中词序 词 词性 支配词序 支配词 支配词性 依存关系
		header.createCell(0).setCellValue("句子编号");
		header.createCell(1).setCellValue("句中词序");
		header.createCell(2).setCellValue("词");
		header.createCell(3).setCellValue("词性");
		header.createCell(4).setCellValue("支配词序");
		header.createCell(5).setCellValue("支配词");
		header.createCell(6).setCellValue("支配词性");
		header.createCell(7).setCellValue("依存关系");
		int pos = 1;
		for (Depend depend : list) {
			System.err.println(pos);
			depend.insertToSheet(sheet, pos++);
		}
	}

	private static String[] splitSentences(String treebank) {
		return treebank.split("\\(ROOT");
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (args.length != 2) {
			System.err.println("Usage:\njava Conv treebank_file output_file");
			System.exit(-1);
		}

		Workbook wb = null;
		if (args[1].endsWith(".xls")) {
			wb = new HSSFWorkbook();
		} else if (args[1].endsWith(".xlsx")) {
			wb = new XSSFWorkbook();
		} else {
			wb = new XSSFWorkbook();
			args[1] += ".xlsx";
		}

		String[] sents = null;
		try {
			sents = readSentences(args[0]);
		} catch (IOException e) {
			e.printStackTrace();
			System.err.println("File open failed.");
			System.exit(-1);
		}

		List<Depend> list = new ArrayList<>();

		int id = 1;
		for (String sent : sents) {
			if (sent.length() <= 1)
				continue;
			list.addAll(Depend.getDepends(sent, id++));
		}

		fillWorkbook(wb, list);

		FileOutputStream fout;
		try {
			fout = new FileOutputStream(args[1]);
			wb.write(fout);
			fout.close();
		} catch (IOException e) {
			e.printStackTrace();
			System.err.println("Output failed.");
			System.exit(-1);
		}

	}

	private static String[] readSentences(String filename)
			throws FileNotFoundException, IOException {
		File inputFile = new File(filename);
		if (!inputFile.exists()) {
			System.err.println("Error! Can't open the file " + filename);
		}
		StringBuffer buffer = new StringBuffer(4096);
		BufferedReader reader = new BufferedReader(new FileReader(inputFile));
		int numRead = 0;
		char[] buf = new char[4096];
		while ((numRead = reader.read(buf)) != -1) {
			buffer.append(buf, 0, numRead);
		}
		reader.close();
		return splitSentences(buffer.toString());
	}

}
