import * as React from "react"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ style, ...props }, ref) => (
    <input
      ref={ref}
      style={{
        width: "100%",
        height: "42px",
        background: "#242f3d",
        border: "1.5px solid #2b3a4a",
        borderRadius: "10px",
        padding: "0 14px",
        color: "#e8f0f8",
        fontSize: "14px",
        outline: "none",
        transition: "border-color 0.2s",
        boxSizing: "border-box",
        fontFamily: "inherit",
        ...style,
      }}
      onFocus={e => (e.currentTarget.style.borderColor = "#2196f3")}
      onBlur={e => (e.currentTarget.style.borderColor = "#2b3a4a")}
      {...props}
    />
  )
)
Input.displayName = "Input"

export { Input }