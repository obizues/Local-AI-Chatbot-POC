import React, { useEffect, useRef } from "react"

interface Props {
  messages: Array<{ user: string, bot: string }>
}

const ChatBox: React.FC<Props> = ({ messages }) => {
  const chatRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages]);

  // Debug: show messages prop as JSON
  const debug = false; // set to true to always show

  return (
    <div
      ref={chatRef}
      style={{
        minHeight: 200,
        height: 350,
        width: "100%",
        overflowY: "auto",
        background: "#fafbfc",
        border: "1px solid #eee",
        borderRadius: 8,
        padding: 8,
        display: "flex",
        flexDirection: "column",
        justifyContent: "flex-end",
        boxSizing: "border-box",
      }}
    >
      {debug && (
        <pre style={{ fontSize: 10, color: 'red' }}>{JSON.stringify(messages, null, 2)}</pre>
      )}
      {messages.length === 0 ? (
        <div style={{ color: '#888', textAlign: 'center', marginTop: 40 }}>
          No messages yet. Start the conversation!
        </div>
      ) : (
        messages.map((msg, i) => (
          <React.Fragment key={i}>
            <div style={{
              background: "#d1e7ff",
              color: "#222",
              padding: "10px 16px",
              borderRadius: "18px 18px 4px 18px",
              marginBottom: 4,
              maxWidth: "70%",
              alignSelf: "flex-end",
              marginLeft: "30%",
              fontWeight: 500,
            }}>
              🧑 <b>You:</b> {msg.user}
            </div>
            <div style={{
              background: "#fff",
              color: "#222",
              padding: "10px 16px",
              borderRadius: "18px 18px 18px 4px",
              marginBottom: 16,
              maxWidth: "70%",
              alignSelf: "flex-end",
              marginLeft: "30%",
            }}>
              🤖 <b>Bot:</b> {msg.bot}
            </div>
          </React.Fragment>
        ))
      )}
    </div>
  );
};

export default ChatBox;
