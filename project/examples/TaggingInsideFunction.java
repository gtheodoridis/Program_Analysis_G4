public class TaggingInsideFunction {
    public static int myFunction(int input3) {
        return 8/input3;
    }

    public static void main(String[] args) {
        int new_var = Integer.parseInt(args[1]); 
        int fail_var = myFunction(new_var); 
    }
}