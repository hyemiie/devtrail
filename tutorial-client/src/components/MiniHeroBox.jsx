import React from 'react'
import './miniHero.css'

export const MiniHeroBox = ({boxDetails}) => {
  return (
    <div className='mini-box'>

        <header>hello</header>
        <div className='box-text'>
        <h1>Simplicity</h1>
        <p className='box-desc'> Automation and full-stack contractor based in Varna </p>
        {/* <p className='sub-box-desc'> Automation and full-stack contractor based in Varna</p> */}
        <ul>
        
            <li>Python</li>
            <li>Python</li>
            <li>Python</li>
            {/* <li>Python</li>
            <li>Python</li>
            <li>Python</li> */}
            {/* <li>Python</li>
            <li>Python</li>
            <li>Python</li> */}
        </ul>
        <div className='code-box'>{}
        <code>hello : "Cape Town ZA"</code><br/>
        <code>hello : "Cape Town ZA"</code><br/>
        {/* <code>hello : "Cape Town ZA"</code> */}
        </div>
      <p className='code-comment'>//  Automation and full-stack contractor based in Varna</p>
    </div>
    </div>
  )
}
