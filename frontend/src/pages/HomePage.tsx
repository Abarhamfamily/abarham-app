import { Link } from 'react-router-dom'

export default function HomePage() {
  return (
    <div>
      <h1>Abarham App</h1>
      <p>به اپلیکیشن ابرهام خوش آمدید.</p>
      <Link to="/trips">مشاهده‌ی تورها</Link>
    </div>
  )
}
