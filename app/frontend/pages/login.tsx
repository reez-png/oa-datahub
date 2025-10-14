import { useState, useEffect } from "react";
import { supabase } from "../lib/supabaseClient";

export default function Login() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState<string|null>(null);

  async function sendLink() {
    setErr(null);
    const { error } = await supabase.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: "http://localhost:3000/auth/callback" }
    });
    if (error) setErr(error.message);
    else setSent(true);
  }

  return (
    <main style={{padding:24, fontFamily:"Inter, system-ui, sans-serif"}}>
      <h1>Sign in</h1>
      <p>We’ll email you a magic link.</p>
      <input value={email} onChange={e=>setEmail(e.target.value)}
             placeholder="you@example.com"
             style={{padding:8, border:"1px solid #ccc", borderRadius:6, width:320}} />
      <div style={{marginTop:12}}>
        <button onClick={sendLink} style={{padding:"8px 12px", border:"1px solid #ccc", borderRadius:6}}>Send link</button>
      </div>
      {sent && <p>Check your email!</p>}
      {err && <p style={{color:"#b00"}}>{err}</p>}
    </main>
  );
}
