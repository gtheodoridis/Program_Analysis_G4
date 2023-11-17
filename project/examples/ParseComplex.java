package dev.fuzzit.examplejava;

public class ParseComplex {
    public static boolean main(String[] args) {
        if (args[0].length() > 4) {
            return false;
        }
        return args[0].charAt(0) == 'F' &&
                args[0].charAt(1) == 'U' &&
                args[0].charAt(2) == 'Z' &&
                args[0].charAt(3) == 'Z';
    }
}