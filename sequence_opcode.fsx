#r "nuget: B2R2.FrontEnd.BinInterface"
open B2R2
open B2R2.FrontEnd.BinInterface
open B2R2.FrontEnd.BinFile
let fileName =
    try fsi.CommandLineArgs.[1]
    with _ -> failwith "File must be given."

// BinHandle is a primary interface for accessing binary code
let hdl = BinHandle.Init (ISA.DefaultISA, fileName)
// Get the text section (assuming there’s only one)
let txtsec = hdl.FileInfo.GetTextSections () |> Seq.head

let mutable ptr = hdl.FileInfo.ToBinaryPointer txtsec.Address
while BinaryPointer.IsValid ptr do
    match BinHandle.TryParseInstr (hdl, bp=ptr) with
    | Ok (ins) ->
        let words = ins.Decompose (false) // Break disassembly into words
        words.[0].AsmWordValue |> printfn "%s"
        ptr <- BinaryPointer.Advance ptr (int ins.Length) // Point to the next instr
    | Error _ -> // When disassembly fails, just advance the pointer by one
        ptr <- BinaryPointer.Advance ptr 1
