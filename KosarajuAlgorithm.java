import java.util.*;

public class KosarajuAlgorithm {

    // Function to perform DFS and record the finishing times
    private static void dfs(Map<String, List<String>> graph, String node, Set<String> visited, Stack<String> stack) {
        visited.add(node);
        for (String neighbor : graph.getOrDefault(node, new ArrayList<>())) {
            if (!visited.contains(neighbor)) {
                dfs(graph, neighbor, visited, stack);
            }
        }
        stack.push(node);
    }

    // Overloaded DFS function to collect nodes in an SCC
    private static void dfsForSCC(Map<String, List<String>> graph, String node, Set<String> visited, List<String> scc) {
        visited.add(node);
        scc.add(node);
        for (String neighbor : graph.getOrDefault(node, new ArrayList<>())) {
            if (!visited.contains(neighbor)) {
                dfsForSCC(graph, neighbor, visited, scc);
            }
        }
    }

    // Function to compute the transpose of the graph
    private static Map<String, List<String>> transposeGraph(Map<String, List<String>> graph) {
        Map<String, List<String>> transposed = new HashMap<>();
        for (String node : graph.keySet()) {
            for (String neighbor : graph.get(node)) {
                transposed.putIfAbsent(neighbor, new ArrayList<>());
                transposed.get(neighbor).add(node);
            }
        }
        return transposed;
    }

    // Function to perform Kosaraju's algorithm
    public static List<List<String>> kosaraju(Map<String, List<String>> graph) {
        Set<String> visited = new HashSet<>();
        Stack<String> stack = new Stack<>();

        // First pass: Fill the stack with finishing times
        for (String node : graph.keySet()) {
            if (!visited.contains(node)) {
                dfs(graph, node, visited, stack);
            }
        }

        // Transpose the graph
        Map<String, List<String>> transposed = transposeGraph(graph);

        // Second pass: Perform DFS on the transposed graph in reverse finishing time order
        visited.clear();
        List<List<String>> sccs = new ArrayList<>();
        while (!stack.isEmpty()) {
            String node = stack.pop();
            if (!visited.contains(node)) {
                List<String> scc = new ArrayList<>();
                dfsForSCC(transposed, node, visited, scc);
                sccs.add(scc);
            }
        }
        return sccs;
    }

    public static void main(String[] args) {
        // Define the graph using an adjacency list
        Map<String, List<String>> graph = new HashMap<>();
        graph.put("A", Arrays.asList("B", "D"));
        graph.put("B", Arrays.asList("C", "E"));
        graph.put("C", Arrays.asList("F"));
        graph.put("D", Arrays.asList("H"));
        graph.put("E", Arrays.asList("H", "A"));
        graph.put("F", Arrays.asList("I"));
        graph.put("G", Arrays.asList("D"));
        graph.put("H", Arrays.asList("G", "F"));
        graph.put("I", Arrays.asList("H"));

        // Run Kosaraju's algorithm
        List<List<String>> sccs = kosaraju(graph);

        // Print the SCCs
        System.out.println("Strongly Connected Components (SCCs):");
        for (List<String> scc : sccs) {
            System.out.println(scc);
        }
    }
}
