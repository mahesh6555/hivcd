import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

public class CalculatePercentIdentityEngine {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		try {
			String inputFile = args[0];
			//String outputFile = args[1];
			String currentSamplesFile = args[1];
			Double percentIdCutoff = Double.parseDouble(args[2]);
			CalculatePercentIdentityEngine ce = new CalculatePercentIdentityEngine();
			
			Long start = System.currentTimeMillis();
			ArrayList<String> currSamples = ce.readCurrentSamplesFile(currentSamplesFile);
			HashMap<String, char[]> seqHash = ce.readAlignmentFile(inputFile);
			Long end = System.currentTimeMillis();
			System.out.println("Time: " + (end - start));
			
			start = System.currentTimeMillis();
			//ce.calculatePercentId(seqHash,currSamples,outputFile,percentIdCutoff);
			ce.calculatePercentId(seqHash,currSamples,percentIdCutoff);
			end = System.currentTimeMillis();
			System.out.println("Time: " + (end - start));
//			for(int i = 0; i < output.size(); i++){
//				System.out.println(output.get(i));
//			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private ArrayList<String> readCurrentSamplesFile(String file) throws IOException{
		System.out.println("Reading current samples file...");
		BufferedReader in = new BufferedReader(new FileReader(file));
		String line;
		ArrayList<String> sampleIds = new ArrayList<String>(); 
		while((line = in.readLine()) != null){
			sampleIds.add(line);
		}
		return sampleIds;
	}
	
	/**
	 * Read in the file of aligned sequences and generate a hashmap
	 * HashMap<String,char[]> of patient id to the patient's aligned sequence
	 * 
	 * @param file
	 * @return HashMap<String,char[]> 
	 * @throws IOException
	 */
	private HashMap<String, char[]> readAlignmentFile(String file) throws IOException{
		System.out.println("Loading seqs...");
		BufferedReader in = new BufferedReader(new FileReader(file));
		String line, seqId = null;
		StringBuilder seq = new StringBuilder();
		HashMap<String, char[]> seqHash = new HashMap<String, char[]>();
		while((line = in.readLine()) != null){
			if(line.contains(">")){
				if(seqId != null){ // If it's null, this is the first sequence in the file
					seq.trimToSize();
					seqHash.put(seqId, seq.toString().toCharArray());
					seq.setLength(0);
				}
				seqId = line.substring(line.indexOf('>') + 1, line.length());
			}
			else if(line.matches("^\\s*$")){
				continue;
			}
			else{
				seq.append(line);
			}
		}
		// Trim and save the last sequence
		seq.trimToSize();
		seqHash.put(seqId, seq.toString().toCharArray());
		seq.setLength(0);
		
		return seqHash;
	}
	
	/**
	 * Calculate the percent identity between samples
	 * 
	 * @param seqHash
	 * @param outFilePath
	 * @param percentIdCutoff
	 * @throws IOException
	 */
	private void calculatePercentId(HashMap<String, char[]> seqHash, ArrayList<String> currSamps, Double percentIdCutoff) throws IOException{
		String[] keys = seqHash.keySet().toArray(new String[0]);
		Arrays.sort(keys);
		String seqId1, seqId2;
		char[] seq1, seq2;
		double length, mismatches;
		double percentId;
		DecimalFormat df = new DecimalFormat("###.##");
//		BufferedWriter out = new BufferedWriter(new FileWriter(outFilePath));
		for(int i = 0; i < currSamps.size(); i++){
			System.out.print( (i+1) + " / " + currSamps.size() + "\r");
			seqId1 = currSamps.get(i);
			seq1 = seqHash.get(seqId1);
			//System.out.println("seqId1:" + seqId1);
			//System.out.println("seq1:" + String.copyValueOf(seq1));
			for(int j = 0; j < keys.length; j++){
				seqId2 = keys[j];
				if(seqId2.equalsIgnoreCase(seqId1)){ // Do not compare to itself
					continue;
				}
				seq2 = seqHash.get(seqId2);			
			//System.out.println("seqId2:" + seqId2);
			//System.out.println("seq2:" + String.copyValueOf(seq2));
				
				length = seq1.length;
				mismatches = 0;
				for(int k = 0; k < seq1.length; k++){
					if(!Character.isLowerCase(seq1[k])){
						seq1[k] = Character.toLowerCase(seq1[k]);
					}
					if(!Character.isLowerCase(seq2[k])){
						seq2[k] = Character.toLowerCase(seq2[k]);
					}
					if(seq1[k] != seq2[k]){
							mismatches++;
					}
					else if(seq1[k] == '-'){ // The previous condition verifies that both seqs match. Only need to check one of the sequences for '-'
						length--;
					}
				}
				percentId = ((length - mismatches)/length) * 100;
				if(percentId >= percentIdCutoff){
					System.out.print(seqId1 + "," + seqId2 + "," + df.format(percentId) + "\n");
//					out.write(seqId1 + "," + seqId2 + "," + df.format(percentId) + "\n");
				}
			}
		}
//		out.close();
	}
}
