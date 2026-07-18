type Props = { small?: boolean }

const pixel = (size: number) => ({ width: size, height: size * 80 / 580 })

export default function Logo({ small }: Props) {
  const dim = small ? pixel(120) : pixel(320)
  return (
    <img
      src="/logo.svg"
      alt="Ghost Screen"
      style={{ display: 'block', ...dim }}
    />
  )
}
