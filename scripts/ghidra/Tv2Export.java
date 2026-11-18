// Exports Ghidra's own view of one analysed program for TV2 evidence.
// Run through scripts/tv2-ghidra.ps1. Argument 0 is the output root.
// Function names written here are Ghidra's names; nothing is renamed by this script.
// @category TV2

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.TreeMap;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.ExternalReference;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.util.DefinedStringIterator;

public class Tv2Export extends GhidraScript {
	private static final Set<String> ROOT_APIS = new HashSet<>(Arrays.asList("CreateFileW", "WriteFile",
		"CloseHandle", "GetProcAddress", "LoadLibraryW", "FreeLibrary"));
	private static final int MAX_DEPTH = 4;

	private long rva(Address address) {
		return address.getOffset() - currentProgram.getImageBase().getOffset();
	}

	private static String csv(String value) {
		return "\"" + (value == null ? "" : value).replace("\"", "\"\"").replace("\r", "\\r").replace("\n", "\\n") + "\"";
	}

	private static String json(String value) {
		return "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
	}

	private PrintWriter open(File file) throws Exception {
		file.getParentFile().mkdirs();
		return new PrintWriter(file, StandardCharsets.UTF_8);
	}

	private String importTarget(Instruction instruction) {
		for (Reference reference : instruction.getReferencesFrom()) {
			if (reference instanceof ExternalReference) {
				return ((ExternalReference) reference).getExternalLocation().getLabel();
			}
			Address to = reference.getToAddress();
			Function function = getFunctionAt(to);
			if (function != null && function.isThunk()) {
				Function thunked = function.getThunkedFunction(true);
				if (thunked != null && thunked.isExternal()) {
					return thunked.getName();
				}
			}
			if (function != null && function.isExternal()) {
				return function.getName();
			}
			Data data = getDataAt(to);
			if (data != null && data.isPointer() && data.getValue() instanceof Address) {
				Symbol symbol = getSymbolAt((Address) data.getValue());
				if (symbol != null && symbol.isExternal()) {
					return symbol.getName();
				}
				for (Reference inner : data.getReferencesFrom()) {
					if (inner instanceof ExternalReference) {
						return ((ExternalReference) inner).getExternalLocation().getLabel();
					}
				}
			}
		}
		return null;
	}

	@Override
	protected void run() throws Exception {
		String[] args = getScriptArgs();
		File out = new File(args[0], currentProgram.getName().replaceAll("\\.exe$", ""));
		TreeMap<Long, Function> selected = new TreeMap<>();
		ArrayDeque<Object[]> queue = new ArrayDeque<>();

		try (PrintWriter calls = open(new File(out, "api-calls.csv"));
				PrintWriter indirect = open(new File(out, "indirect-calls.csv"))) {
			calls.println("caller_entry_rva,caller,call_rva,instruction,target_api");
			indirect.println("caller_entry_rva,caller,call_rva,instruction");
			InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
			while (instructions.hasNext() && !monitor.isCancelled()) {
				Instruction instruction = instructions.next();
				if (!instruction.getFlowType().isCall()) {
					continue;
				}
				Function caller = getFunctionContaining(instruction.getAddress());
				String callerName = caller == null ? "" : caller.getName();
				String callerRva = caller == null ? "" : String.format("0x%X", rva(caller.getEntryPoint()));
				String target = importTarget(instruction);
				String where = String.format("%s,%s,0x%X,%s", callerRva, csv(callerName), rva(instruction.getAddress()),
					csv(instruction.toString()));
				if (target != null) {
					calls.println(where + "," + csv(target));
					if (ROOT_APIS.contains(target) && caller != null) {
						queue.add(new Object[] { caller, 0 });
					}
				}
				else if (instruction.getFlowType().isComputed() && instruction.getMnemonicString().equals("CALL")) {
					indirect.println(where);
				}
			}
		}

		while (!queue.isEmpty()) {
			Object[] item = queue.poll();
			Function function = (Function) item[0];
			int depth = (Integer) item[1];
			long key = rva(function.getEntryPoint());
			if (selected.containsKey(key) || function.isThunk() || function.isExternal()) {
				continue;
			}
			selected.put(key, function);
			if (depth < MAX_DEPTH) {
				for (Function callee : function.getCalledFunctions(monitor)) {
					queue.add(new Object[] { callee, depth + 1 });
				}
			}
		}

		try (PrintWriter imports = open(new File(out, "imports.csv"))) {
			imports.println("library,symbol,reference_addresses");
			SymbolIterator symbols = currentProgram.getSymbolTable().getExternalSymbols();
			while (symbols.hasNext()) {
				Symbol symbol = symbols.next();
				StringBuilder refs = new StringBuilder();
				for (Reference reference : symbol.getReferences()) {
					refs.append(String.format("0x%X ", rva(reference.getFromAddress())));
				}
				imports.println(csv(symbol.getParentNamespace().getName()) + "," + csv(symbol.getName()) + "," +
					csv(refs.toString().trim()));
			}
		}

		try (PrintWriter strings = open(new File(out, "strings.csv"))) {
			strings.println("rva,type,value,referenced_from_rva");
			for (Data data : DefinedStringIterator.forProgram(currentProgram)) {
				String value = StringDataInstance.getStringDataInstance(data).getStringValue();
				StringBuilder refs = new StringBuilder();
				for (Reference reference : getReferencesTo(data.getAddress())) {
					refs.append(String.format("0x%X ", rva(reference.getFromAddress())));
				}
				strings.println(String.format("0x%X,%s,%s,%s", rva(data.getAddress()), csv(data.getDataType().getName()),
					csv(value), csv(refs.toString().trim())));
			}
		}

		try (PrintWriter functions = open(new File(out, "functions.csv"))) {
			functions.println("entry_rva,ghidra_name,size,is_thunk,exported_for_review");
			for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
				long key = rva(function.getEntryPoint());
				functions.println(String.format("0x%X,%s,%d,%s,%s", key, csv(function.getName()),
					function.getBody().getNumAddresses(), function.isThunk(), selected.containsKey(key)));
			}
		}

		DecompInterface decompiler = new DecompInterface();
		decompiler.openProgram(currentProgram);
		for (Function function : selected.values()) {
			String stem = String.format("%s_rva_%X", function.getName(), rva(function.getEntryPoint()));
			DecompileResults result = decompiler.decompileFunction(function, 120, monitor);
			try (PrintWriter writer = open(new File(out, "decompile/" + stem + ".c"))) {
				writer.println(result.decompileCompleted() ? result.getDecompiledFunction().getC()
						: "// decompilation failed: " + result.getErrorMessage());
			}
			try (PrintWriter writer = open(new File(out, "disasm/" + stem + ".asm"))) {
				InstructionIterator body = currentProgram.getListing().getInstructions(function.getBody(), true);
				while (body.hasNext()) {
					Instruction instruction = body.next();
					writer.println(String.format("RVA_%08X  %s", rva(instruction.getAddress()), instruction));
				}
			}
		}
		decompiler.dispose();

		try (PrintWriter summary = open(new File(out, "summary.json"))) {
			summary.println("{");
			summary.println("  \"tool\": \"Ghidra " + Application.getApplicationVersion() + "\",");
			summary.println("  \"program\": " + json(currentProgram.getName()) + ",");
			summary.println("  \"sha256\": " + json(currentProgram.getExecutableSHA256().toUpperCase()) + ",");
			summary.println("  \"image_base\": " + json(currentProgram.getImageBase().toString()) + ",");
			summary.println("  \"language\": " + json(currentProgram.getLanguageID().getIdAsString()) + ",");
			summary.println("  \"compiler_spec\": " + json(currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString()) + ",");
			summary.println("  \"function_count\": " + currentProgram.getFunctionManager().getFunctionCount() + ",");
			summary.println("  \"functions_exported_for_review\": " + selected.size());
			summary.println("}");
		}
		println("TV2 export finished: " + out.getAbsolutePath());
	}
}
