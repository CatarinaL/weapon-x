import Head from 'next/head'
import Image from 'next/image'
import styles from '../styles/Home.module.css'

import useSWR from 'swr'
import React from 'react';
import {Doughnut} from 'react-chartjs-2';

const fetcher = (...args) => fetch(...args).then(res => res.json())


const graph_data = (predictions) => ({
  labels: [
    'Normal',
    'Machine Down',
    'Disk Full',
    'Network Disconnect'
  ],
  datasets: [{
    data: [
      predictions.normal,
      predictions.machine_down,
      predictions.network_disconnect,
      predictions.disk_full,
    ],
    backgroundColor: [
    '#4BC0C0',
    '#FF6384',
    '#36A2EB',
    '#FFCE56',
    ],
    hoverBackgroundColor: [
    '#4BC0C0',
    '#FF6384',
    '#36A2EB',
    '#FFCE56',
    ]
  }]
});


export default function Home() {

  const { data, error } = useSWR('http://fyp-lb-1908393187.eu-west-1.elb.amazonaws.com/processed', fetcher)

  if (error) {
    return ("Unexpected error loading log results")
  } 
  if (!data) {
    return ("Loading...")
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>Log analysis results</title>
        <meta name="description" content="List of recently analysed logs" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Recently analysed logs
        </h1>

        <div className={styles.grid}>

          {
            data.slice(0, 10).reverse().map(
              (item, i) => 
                <div className={styles.card}>
                  <h2>{item.filename} &rarr;</h2>
                  <Doughnut
                    data={graph_data(item.result.predictions)}
                    width={300}
                    height={300}
                  />
                </div>
            )
            
          }

        </div>
      </main>

      <footer className={styles.footer}>
        <a
          href="https://vercel.com?utm_source=create-next-app&utm_medium=default-template&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          Powered by{' '}
          <span className={styles.logo}>
            <Image src="/vercel.svg" alt="Vercel Logo" width={72} height={16} />
          </span>
        </a>
      </footer>
    </div>
  )
}

