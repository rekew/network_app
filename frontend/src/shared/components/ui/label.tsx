import * as React from "react"

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ style, ...props }, ref) => (
    <label
      ref={ref}
      style={{
        display: "block",
        color: "#8ba4b8",
        fontSize: "11px",
        fontWeight: 700,
        letterSpacing: "0.07em",
        textTransform: "uppercase",
        marginBottom: "7px",
        ...style,
      }}
      {...props}
    />
  )
)
Label.displayName = "Label"

export { Label }