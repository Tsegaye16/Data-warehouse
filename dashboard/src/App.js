import React, { useState } from "react";
import { Tabs, Alert } from "antd";
import PreProcessedTable from "./components/PreProcessedTable";
import RawDataTable from "./components/RawDataTable";
import { useMessages } from "./hooks/useMessages";
import { useRawMessages } from "./hooks/useRawMessages";

function App() {
  const [activeTab, setActiveTab] = useState("preProcessed");

  const { error: errorMessages } = useMessages();
  const { error: errorRaw } = useRawMessages();

  return (
    <div className="App">
      <header className="App-header">
        <h1>Message Table</h1>
      </header>
      {errorMessages || errorRaw ? (
        <Alert
          message="Error"
          description={errorMessages || errorRaw}
          type="error"
          showIcon
        />
      ) : (
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <Tabs.TabPane tab="Pre-processed Data" key="preProcessed">
            <PreProcessedTable />
          </Tabs.TabPane>
          <Tabs.TabPane tab="Raw Data" key="rawData">
            <RawDataTable />
          </Tabs.TabPane>
        </Tabs>
      )}
    </div>
  );
}

export default App;
