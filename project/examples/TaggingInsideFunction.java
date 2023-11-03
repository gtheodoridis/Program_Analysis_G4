public class TaggingInsideFunction {
    public static int myFunction(int input3) {
        return 8/input3;
    }

    public static void main(int input, int input2) {
        int new_var = input2; 
        int fail_var = myFunction(new_var); 
    }
}