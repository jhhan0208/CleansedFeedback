def final_labeling(df):

    final_hate = []
    final_feedback = []

    for _, row in df.iterrows():

        if row['M_Label'] == 'clean': x = 'clean'
        else:
            x = 'hate'
        final_hate.append(x)

        """
        if (row['M_Label'] == 'hate' and row['M_Score'] > 0.8) or (row['M_Label'] == 'offensive' and row['M_Score'] > 0.7): # 0.8 0.7
            x = 'hate'
        else:
            x = 'clean'
        final_hate.append(x)
        """

        y = row['F_Label']
        final_feedback.append(y)
        
    df['final_hate'] = final_hate 
    df['final_feedback'] = final_feedback

    return df

