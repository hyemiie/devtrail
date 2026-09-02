import React from 'react'
import { HeroBox } from '../components/HeroBox'
import './Home.css'
import { MiniHeroBox } from '../components/MiniHeroBox'
const Home = () => {
  return (
    <div className='hero'>
    <HeroBox/>
    <MiniHeroBox/>
    <div className='miniHeroDiv'>
    <MiniHeroBox/>
    </div>
    </div>
  )
}

export default Home