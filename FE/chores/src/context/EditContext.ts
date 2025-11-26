import { createContext, createElement, useState } from "react";
import type { ReactNode } from "react";

type EditPanelDayInfo = {
  id : number,
  dayOfWeek : string,
  shift : 'Morning' | 'Evening'
}

type EditPanelContextType = {
  showEditPanel: EditPanelDayInfo | undefined;
  setEditPanelState: (state: EditPanelDayInfo | undefined) => void;
};

const editPanelContext = createContext<EditPanelContextType>({
  showEditPanel: undefined,
  setEditPanelState: () => {},
});

function EditPanelProvider({ children }: { children: ReactNode }) {
  const [showEditPanel, setEditPanelState] = useState<EditPanelDayInfo | undefined>(
    undefined,
  );

  return createElement(
    editPanelContext.Provider,
    { value: { showEditPanel, setEditPanelState } },
    children,
  );
}

export { editPanelContext, EditPanelProvider };
