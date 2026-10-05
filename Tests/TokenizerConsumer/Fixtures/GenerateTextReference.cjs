const fs = require('fs');
const path = require('path');
const consumer = path.resolve(__dirname, '..');
if (process.version !== 'v23.2.0' || process.versions.unicode !== '16.0') {
  throw new Error('Reference regeneration requires Node v23.2.0 / Unicode 16.0');
}
const inputs = ["", "we're  ici\n\t ", "I'm I'M he'll SHE'S don't I've we'd", "Hello, 世界 １２３ Ⅳ² مرحبا 👩‍💻!", "e\u0301é", "a\0b", "  hello  ", " \tx", " \t x", "\r\nx\n\n", " \t\r\n", "a\u00a0b\u0085c\u2003d\u202fe\ufefff", "e\u0301é \u1100\u1161", "ﬁ ＡＢＣ ① ¼", "ﷺ", "\u0009\u000a\u000b\u000c\u000d\u0020\u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000", "a\u001cb\u200bc\u180ed"];
const originalPattern = "'s|'t|'re|'ve|'m|'ll|'d| ?\\p{L}+| ?\\p{N}+| ?[^\\s\\p{L}\\p{N}]+|\\s+(?!\\S)|\\s+";
// ECMAScript \s differs from Unicode White_Space. Explicit properties retain
// the GPT-2 Python regex semantics; the production Silex motif is unchanged.
const referencePattern = originalPattern.replaceAll('\\s','\\p{White_Space}').replaceAll('\\S','\\P{White_Space}');
const regex = new RegExp(referencePattern, 'gu');
let lines=[];
for (let mode=0;mode<3;mode++) for(let profile=0;profile<2;profile++) inputs.forEach((raw,index)=>{
 const text=mode===0?raw:raw.normalize(mode===1?'NFC':'NFKC');
 const bytes=Buffer.from(text,'utf8');
 lines.push(`case ${mode}:${profile}:${index}`,`bytes ${bytes.length}`);
 bytes.forEach((id,index)=>lines.push(`${id}:${index}:${index+1}`));
 if(profile===0){if(bytes.length)lines.push(`segment 0:${bytes.length}`);}
 else for(const match of text.matchAll(regex)) {
  const start=Buffer.byteLength(text.slice(0,match.index),'utf8');
  lines.push(`segment ${start}:${start+Buffer.byteLength(match[0],'utf8')}`);
 }
});
fs.writeFileSync(consumer+'/Fixtures/text-pipeline-reference.txt',lines.join('\n')+'\n');
fs.writeFileSync(consumer+'/Fixtures/text-pipeline-reference.meta.json',JSON.stringify({node:process.version,unicode:process.versions.unicode,v8:process.versions.v8,originalPattern,referencePattern,cases:inputs.length,configurations:6,source:'https://huggingface.co/transformers/v2.10.0/_modules/transformers/tokenization_gpt2.html',scope:'Selected stable-character pre-tokenization and normalization fixtures; not a complete BPE/tokenizer oracle.'},null,2)+'\n');
function sxString(s){return JSON.stringify(s).replaceAll('\\f','\\u{000c}').replaceAll('\\b','\\u{0008}').replace(/[\u0085\u2028\u2029\ufeff]/g,c=>'\\u{'+c.codePointAt(0).toString(16)+'}').replace(/\\u([0-9a-fA-F]{4})/g,(_,hex)=>'\\u{'+hex+'}');}
const source=`use AI.Tokenizer

// Selected fixtures independently evaluated by Node/V8, not a full BPE oracle.
func main() {
    let inputs:str[] = [${inputs.map(sxString).join(',\n        ')}]
    let modes:Tokenizer.Normalization[] = [Tokenizer.Normalization.identity, Tokenizer.Normalization.nfc, Tokenizer.Normalization.nfkc]
    let profiles:Tokenizer.PreTokenizer[] = [Tokenizer.PreTokenizer.none, Tokenizer.PreTokenizer.gpt2]
    var mode_index = 0
    for mode in modes {
        var profile_index = 0
        for profile in profiles {
            var tokenizer = try Tokenizer.parse_bpe(embed_text("Fixtures/vocab.json"), "",
                Tokenizer.LoadOptions(normalization:mode, pre_tokenizer:profile)) else error { panic(error.detail) }
            var case_index = 0
            for input in inputs {
                let encoding = try tokenizer.encode(input) else error { panic(error.detail) }
                let decoded = try tokenizer.decode(encoding.ids()) else error { panic(error.detail) }
                assert(decoded == encoding.normalized_text())
                print("case $(mode_index):$(profile_index):$(case_index)")
                print("bytes $(encoding.count())")
                for piece in encoding.pieces() {
                    print("$(piece.id):$(piece.span!.start):$(piece.span!.end)")
                }
                for boundary in encoding.segments() { print("segment $(boundary.start):$(boundary.end)") }
                case_index++
            }
            profile_index++
        }
        mode_index++
    }
}
`;
fs.writeFileSync(consumer+'/TextPipelineParity.sx',source);
