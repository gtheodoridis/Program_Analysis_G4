public class SplittingInput {
    public static void main(String[] args) {
        
        String input = args[1];
        
        // Split the input into two halves
        String new_var = input.substring(0, input.length() / 2);
        
        // Attempting to access an index outside the bounds of the new_var
        char invalidAccess = new_var.charAt(input.length() - 1);
    }
}
