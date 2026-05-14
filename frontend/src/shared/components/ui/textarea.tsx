import * as React from "react"

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ style, ...props }, ref) => (
    <textarea
      ref={ref}
      style={{
        width: "100%",
        minHeight: "80px",
        background: "#242f3d",
        border: "1.5px solid #2b3a4a",
        borderRadius: "10px",
        padding: "11px 14px",
        color: "#e8f0f8",
        fontSize: "14px",
        outline: "none",
        transition: "border-color 0.2s",
        boxSizing: "border-box",
        fontFamily: "inherit",
        resize: "none",
        ...style,
      }}
      onFocus={e => (e.currentTarget.style.borderColor = "#2196f3")}
      onBlur={e => (e.currentTarget.style.borderColor = "#2b3a4a")}
      {...props}
    />
  )
)
Textarea.displayName = "Textarea"

export { Textarea }