public class IndirectUsageIf {
    public static void main(String[] args) {
        int new_var;
        if (Integer.parseInt(args[0]) > 0) {
            new_var = 2 / 0; 
        }
    }
}